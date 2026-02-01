from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx


@dataclass
class OcrResult:
    job_id: str
    status: str
    artifacts: dict[str, Any]
    metadata: dict[str, Any]
    error: dict[str, Any] | None = None


class OcrClient:
    def __init__(self, base_url: str, transport: httpx.BaseTransport | None = None) -> None:
        self._client = httpx.Client(base_url=base_url, transport=transport, timeout=60.0)

    def __enter__(self) -> "OcrClient":
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()

    def submit_pdf(
        self,
        file_path: str,
        run_id: str,
        document_id: str,
        parser_profile: str,
        callback_url: str,
        options: dict[str, Any] | None = None,
    ) -> str:
        pdf_path = Path(file_path)
        with pdf_path.open("rb") as handle:
            files = {"file": (pdf_path.name, handle, "application/pdf")}
            data = {
                "run_id": run_id,
                "document_id": document_id,
                "parser_profile": parser_profile,
                "callback_url": callback_url,
            }
            if options:
                for key, value in options.items():
                    if value is None:
                        continue
                    if isinstance(value, bool):
                        data[key] = "true" if value else "false"
                    else:
                        data[key] = str(value)
            response = self._client.post("/v1/ocr", data=data, files=files)
        response.raise_for_status()
        payload = response.json()
        job_id = payload.get("job_id")
        if not job_id:
            raise ValueError(f"Missing job_id in OCR response: {payload}")
        return job_id

    def get_status(self, job_id: str) -> dict[str, Any]:
        response = self._client.get(f"/v1/ocr/{job_id}")
        response.raise_for_status()
        return response.json()

    def get_result(self, job_id: str) -> OcrResult:
        response = self._client.get(f"/v1/ocr/{job_id}/result")
        response.raise_for_status()
        payload = response.json()
        return OcrResult(
            job_id=payload["job_id"],
            status=payload["status"],
            artifacts=payload.get("artifacts", {}),
            metadata=payload.get("metadata", {}),
            error=payload.get("error"),
        )
