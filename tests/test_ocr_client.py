from pathlib import Path

import httpx
import pytest

from dealsignals.parsing.ocr_client import OcrClient


@pytest.fixture
def mock_transport():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["request"] = request
        captured["body"] = request.read()
        return httpx.Response(200, json={"job_id": "job_abc"})

    transport = httpx.MockTransport(handler)
    transport.captured = captured
    return transport


def build_transport(status_code: int, json_payload: dict | None = None) -> httpx.MockTransport:
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["request"] = request
        return httpx.Response(status_code, json=json_payload)

    transport = httpx.MockTransport(handler)
    transport.captured = captured
    return transport


def test_submit_job_uses_expected_payload(tmp_path, mock_transport):
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 sample")

    with OcrClient(base_url="http://localhost:8000", transport=mock_transport) as client:
        job_id = client.submit_pdf(
            file_path=str(pdf_path),
            run_id="run_123",
            document_id="doc_456",
            parser_profile="ocrmypdf_tesseract_v1",
            callback_url="http://localhost/callback",
        )

    assert job_id == "job_abc"

    request = mock_transport.captured["request"]
    body = mock_transport.captured["body"]

    assert request.method == "POST"
    assert str(request.url) == "http://localhost:8000/v1/ocr"
    assert request.headers["content-type"].startswith("multipart/form-data")
    assert b'name="run_id"' in body
    assert b'name="document_id"' in body
    assert b'name="parser_profile"' in body
    assert b'name="callback_url"' in body
    assert b'name="file"' in body
    assert b"run_123" in body
    assert b"doc_456" in body
    assert b"ocrmypdf_tesseract_v1" in body
    assert b"http://localhost/callback" in body
    assert b"sample.pdf" in body


def test_submit_pdf_includes_options(tmp_path, mock_transport):
    pdf_path = tmp_path / "sample-options.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 sample")

    with OcrClient(base_url="http://localhost:8000", transport=mock_transport) as client:
        job_id = client.submit_pdf(
            file_path=str(pdf_path),
            run_id="run_123",
            document_id="doc_456",
            parser_profile="ocrmypdf_tesseract_v1",
            callback_url="http://localhost/callback",
            options={"skip_text": True, "force_ocr": False},
        )

    assert job_id == "job_abc"
    body = mock_transport.captured["body"]
    assert b'name="skip_text"' in body
    assert b'name="force_ocr"' in body
    assert b"true" in body
    assert b"false" in body


def test_submit_pdf_raises_when_job_id_missing(tmp_path):
    transport = build_transport(200, {"status": "queued"})
    pdf_path = tmp_path / "missing-job.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 sample")

    with OcrClient(base_url="http://localhost:8000", transport=transport) as client:
        with pytest.raises(ValueError, match="Missing job_id") as excinfo:
            client.submit_pdf(
                file_path=str(pdf_path),
                run_id="run_123",
                document_id="doc_456",
                parser_profile="ocrmypdf_tesseract_v1",
                callback_url="http://localhost/callback",
            )

    assert "queued" in str(excinfo.value)


def test_get_status_parses_json():
    transport = build_transport(200, {"job_id": "job_123", "status": "running"})

    with OcrClient(base_url="http://localhost:8000", transport=transport) as client:
        status = client.get_status("job_123")

    assert status == {"job_id": "job_123", "status": "running"}
    request = transport.captured["request"]
    assert request.method == "GET"
    assert str(request.url) == "http://localhost:8000/v1/ocr/job_123"


def test_get_result_parses_json():
    payload = {
        "job_id": "job_123",
        "status": "done",
        "artifacts": {"text": "hello"},
        "metadata": {"pages": 2},
        "error": None,
    }
    transport = build_transport(200, payload)

    with OcrClient(base_url="http://localhost:8000", transport=transport) as client:
        result = client.get_result("job_123")

    assert result.job_id == "job_123"
    assert result.status == "done"
    assert result.artifacts == {"text": "hello"}
    assert result.metadata == {"pages": 2}
    assert result.error is None
    request = transport.captured["request"]
    assert request.method == "GET"
    assert str(request.url) == "http://localhost:8000/v1/ocr/job_123/result"


def test_get_status_raises_for_error_response():
    transport = build_transport(500, {"detail": "server error"})

    with OcrClient(base_url="http://localhost:8000", transport=transport) as client:
        with pytest.raises(httpx.HTTPStatusError):
            client.get_status("job_123")


def test_client_close_closes_httpx_client():
    transport = build_transport(200, {"job_id": "job_123", "status": "running"})
    client = OcrClient(base_url="http://localhost:8000", transport=transport)

    assert client._client.is_closed is False
    client.close()
    assert client._client.is_closed is True


def test_client_context_manager_closes_httpx_client():
    transport = build_transport(200, {"job_id": "job_123", "status": "running"})

    with OcrClient(base_url="http://localhost:8000", transport=transport) as client:
        assert client._client.is_closed is False

    assert client._client.is_closed is True
