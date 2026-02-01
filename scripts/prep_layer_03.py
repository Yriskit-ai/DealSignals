import json
import logging
import os
import shutil
import time
from pathlib import Path

from dealsignals.parsing.ocr_client import OcrClient


def build_document_text(pages_path: Path) -> str:
    logger = logging.getLogger(__name__)
    lines: list[str] = []
    for line_number, raw_line in enumerate(
        pages_path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not raw_line.strip():
            continue
        try:
            page = json.loads(raw_line)
        except json.JSONDecodeError:
            logger.warning("Skipping malformed JSONL line %s", line_number)
            continue
        if not isinstance(page, dict) or "page" not in page or "text" not in page:
            logger.warning(
                "Skipping page entry missing keys: page, text on line %s",
                line_number,
            )
            continue
        page_number = page["page"]
        page_text = str(page["text"]).strip()
        lines.append(f"[Page {page_number}]\n{page_text}\n")
    return "\n".join(lines).strip()


def _require_env(name: str) -> str | None:
    value = os.environ.get(name)
    if value:
        return value
    print(f"Error: {name} is required.")
    return None


def _read_float_env(name: str, default: float) -> float:
    value = os.environ.get(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"Invalid {name} value: {value}") from exc


def _read_bool_env(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False
    raise ValueError(f"Invalid {name} value: {value}")


def _wait_for_completion(
    client: OcrClient,
    job_id: str,
    poll_interval_s: float,
    timeout_s: float,
) -> str:
    start = time.monotonic()
    interval = poll_interval_s
    while True:
        try:
            status_payload = client.get_status(job_id)
        except Exception as exc:
            raise RuntimeError(f"Failed to fetch OCR status for job {job_id}.") from exc
        status = status_payload.get("status")
        if status in {"succeeded", "failed"}:
            return str(status)
        if status not in {"queued", "running"}:
            raise RuntimeError(f"Unknown OCR status '{status}' for job {job_id}.")
        if time.monotonic() - start >= timeout_s:
            raise TimeoutError(f"OCR job {job_id} timed out after {timeout_s:.0f} seconds.")
        time.sleep(interval)
        interval = min(interval * 1.5, max(poll_interval_s * 5, interval))


def _copy_artifacts(
    artifacts: dict[str, object],
    output_dir: Path,
    document_id: str,
) -> dict[str, Path]:
    mapping = {
        "searchable_pdf_path": f"{document_id}_searchable.pdf",
        "text_path": f"{document_id}_ocr.txt",
        "pages_path": f"{document_id}_pages.jsonl",
        "meta_path": f"{document_id}_meta.json",
    }
    copied: dict[str, Path] = {}
    for key, filename in mapping.items():
        source_value = artifacts.get(key)
        if not source_value:
            continue
        source_path = Path(str(source_value))
        if not source_path.exists():
            raise FileNotFoundError(f"Artifact {key} not found at {source_path}")
        destination = output_dir / filename
        shutil.copy(source_path, destination)
        copied[key] = destination
    return copied


def main(client: OcrClient | None = None, sleep_seconds: float | None = None) -> int:
    base_url = os.environ.get("LAYER_03_BASE_URL", "http://localhost:8000")
    output_dir_value = os.environ.get("LAYER_03_OUTPUT_DIR")
    if output_dir_value:
        output_dir = Path(output_dir_value)
    else:
        output_dir = Path("experiments/wework-bowx/data/layer-03/ocrmypdf_tesseract_v1")
    poll_interval = _read_float_env("LAYER_03_POLL_INTERVAL_S", 2.0)
    poll_timeout = _read_float_env("LAYER_03_POLL_TIMEOUT_S", 3600.0)
    skip_text = _read_bool_env("LAYER_03_SKIP_TEXT", False)
    force_ocr = _read_bool_env("LAYER_03_FORCE_OCR", False)
    if sleep_seconds is not None:
        poll_interval = sleep_seconds

    s4_path_value = _require_env("LAYER_03_S4_PDF_PATH")
    investor_path_value = _require_env("LAYER_03_INVESTOR_PDF_PATH")
    if not s4_path_value or not investor_path_value:
        return 1

    documents = {
        "s4": Path(s4_path_value),
        "investor_presentation": Path(investor_path_value),
    }

    for document_id, path in documents.items():
        if not path.exists():
            print(f"Error: PDF not found for {document_id}: {path}")
            return 1

    output_dir.mkdir(parents=True, exist_ok=True)
    parser_profile = "ocrmypdf_tesseract_v1"
    run_id = "layer-03"
    callback_url = f"{base_url}/v1/ocr/callback"
    options: dict[str, bool] = {}
    if skip_text:
        options["skip_text"] = True
    if force_ocr:
        options["force_ocr"] = True

    def process_document(
        client_instance: OcrClient,
        document_id: str,
        path: Path,
        submit_options: dict[str, bool],
    ) -> int:
        try:
            job_id = client_instance.submit_pdf(
                file_path=str(path),
                run_id=run_id,
                document_id=document_id,
                parser_profile=parser_profile,
                callback_url=callback_url,
                options=submit_options or None,
            )
        except Exception as exc:
            raise RuntimeError(f"OCR submit failed for {document_id}.") from exc
        status = _wait_for_completion(client_instance, job_id, poll_interval, poll_timeout)
        if status != "succeeded":
            print(f"Error: OCR job {job_id} failed with status {status}.")
            return 1
        try:
            result = client_instance.get_result(job_id)
        except Exception as exc:
            raise RuntimeError(f"OCR result fetch failed for job {job_id}.") from exc
        if result.status != "succeeded":
            print(f"Error: OCR job {job_id} failed with status {result.status}.")
            return 1
        copied = _copy_artifacts(result.artifacts, output_dir, document_id)
        pages_path = copied.get("pages_path")
        if not pages_path:
            print(f"Error: Missing pages artifact for {document_id}.")
            return 1
        document_text = build_document_text(pages_path)
        output_path = output_dir / f"{document_id}_text.txt"
        output_path.write_text(document_text, encoding="utf-8")
        return 0

    if client is None:
        with OcrClient(base_url=base_url) as live_client:
            for document_id, path in documents.items():
                if process_document(live_client, document_id, path, options) != 0:
                    return 1
    else:
        for document_id, path in documents.items():
            if process_document(client, document_id, path, options) != 0:
                return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
