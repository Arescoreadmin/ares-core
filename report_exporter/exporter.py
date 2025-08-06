"""Utilities for exporting logs as signed reports and uploading them to S3."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable, Optional
import csv
import hmac
import hashlib
import json
import tempfile

try:
    import requests
except Exception:  # pragma: no cover - requests is optional for tests
    requests = None  # type: ignore


def fetch_logs(base_url: str, start: str, end: str) -> list[dict]:
    """Fetch logs from the log_indexer service."""
    if requests is None:
        raise RuntimeError("requests library is required for fetch_logs")
    resp = requests.get(f"{base_url}/logs", params={"start": start, "end": end}, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if isinstance(data, dict):
        # some indexers might wrap the result
        data = data.get("logs", [])
    return list(data)


def generate_csv(logs: Iterable[dict], output_path: Path) -> Path:
    """Generate a CSV report from log entries."""
    logs = list(logs)
    if not logs:
        headers: list[str] = []
    else:
        headers = list(logs[0].keys())
    with output_path.open("w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        for row in logs:
            writer.writerow(row)
    return output_path


def generate_pdf(logs: Iterable[dict], output_path: Path) -> Path:
    """Generate a simple PDF report from log entries.

    Requires the optional ``fpdf2`` package. If the package is not available,
    ``RuntimeError`` is raised.
    """
    try:
        from fpdf import FPDF  # type: ignore
    except Exception as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("fpdf2 package is required for PDF generation") from exc

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Log Report", ln=True, align="C")
    pdf.ln(10)
    for entry in logs:
        line = json.dumps(entry)
        pdf.multi_cell(0, 10, txt=line)
    pdf.output(str(output_path))
    return output_path


def sign_file(file_path: Path, secret_key: bytes, signature_path: Optional[Path] = None) -> Path:
    """Sign a file using HMAC-SHA256."""
    with file_path.open("rb") as f:
        data = f.read()
    signature = hmac.new(secret_key, data, hashlib.sha256).hexdigest()
    if signature_path is None:
        signature_path = file_path.with_suffix(file_path.suffix + ".sig")
    with signature_path.open("w") as f:
        f.write(signature)
    return signature_path


def upload_to_s3(
    file_path: Path,
    bucket: str,
    object_name: str,
    *,
    retention_days: int = 1,
    s3_client: Optional[object] = None,
) -> None:
    """Upload ``file_path`` to S3 with basic immutability settings.

    ``s3_client`` can be provided for testing to avoid requiring boto3.
    """
    if s3_client is None:
        try:  # pragma: no cover - requires boto3 which is optional in tests
            import boto3
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("boto3 is required for S3 uploads") from exc
        s3_client = boto3.client("s3")

    retain_until = datetime.utcnow() + timedelta(days=retention_days)
    with file_path.open("rb") as data:
        s3_client.put_object(
            Bucket=bucket,
            Key=object_name,
            Body=data,
            ObjectLockMode="COMPLIANCE",
            ObjectLockRetainUntilDate=retain_until,
        )


@dataclass
class ExportConfig:
    """Configuration for exporting logs."""

    log_indexer_url: str
    bucket: str
    secret_key: bytes


def export_reports(config: ExportConfig, start: str, end: str) -> dict:
    """High-level helper to fetch logs and export reports."""
    logs = fetch_logs(config.log_indexer_url, start, end)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        csv_path = generate_csv(logs, tmpdir_path / "report.csv")
        pdf_path = generate_pdf(logs, tmpdir_path / "report.pdf")

        csv_sig = sign_file(csv_path, config.secret_key)
        pdf_sig = sign_file(pdf_path, config.secret_key)

        upload_to_s3(csv_path, config.bucket, f"reports/{csv_path.name}")
        upload_to_s3(csv_sig, config.bucket, f"reports/{csv_sig.name}")
        upload_to_s3(pdf_path, config.bucket, f"reports/{pdf_path.name}")
        upload_to_s3(pdf_sig, config.bucket, f"reports/{pdf_sig.name}")

        return {
            "csv": csv_path,
            "csv_signature": csv_sig,
            "pdf": pdf_path,
            "pdf_signature": pdf_sig,
        }
