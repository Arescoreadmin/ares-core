import csv
import json
import zipfile
from datetime import datetime
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from fpdf import FPDF

from .logging_config import setup_logging, load_env

logger = setup_logging()


_session = requests.Session()
_adapter = HTTPAdapter(max_retries=Retry(total=3, backoff_factor=0.5))
_session.mount("http://", _adapter)
_session.mount("https://", _adapter)


def fetch_logs():
    logger.info("fetch_logs")
    log_indexer_url = load_env("LOG_INDEXER_URL")
    resp = _session.get(f"{log_indexer_url}/export", timeout=5)
    resp.raise_for_status()
    return resp.json()


def generate_csv(logs, filename: Path | str) -> None:
    """Serialize *logs* to ``filename`` in CSV format.

    Each log is a mapping with ``message`` and ``level`` keys.  The writer uses
    ``\n`` as the line terminator for consistent output across platforms.
    """
    logger.info("generate_csv", extra={"file": str(filename)})
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["message", "level"], lineterminator="\n"
        )
        writer.writeheader()
        for log in logs:
            writer.writerow(
                {"message": log.get("message"), "level": log.get("level")}
            )

def generate_pdf(logs, filename):
    """Write logs to a PDF file."""
    logger.info("generate_pdf", extra={"file": str(filename)})
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    for log in logs:
        line = f"{log['timestamp']} {log['level']} {log['service']} {log['message']}"
        pdf.multi_cell(0, 10, line)
    pdf.output(filename)


def hash_file(path: Path | str) -> Path:
    """Compute the SHA-256 hash of ``path`` and write it to ``<path>.sha256``."""
    import hashlib

    file_path = Path(path)
    digest = hashlib.sha256(file_path.read_bytes()).hexdigest()
    hash_path = file_path.with_suffix(file_path.suffix + ".sha256")
    hash_path.write_text(digest)
    logger.info("hash_file", extra={"file": str(file_path)})
    return hash_path


def sign_file(path: Path | str, key: bytes) -> Path:
    """Return the path to a detached HMAC signature for ``path``.

    The file's contents are read and signed using SHA-256.  The hexadecimal
    digest is written to a sibling file with the ``.sig`` suffix.
    """
    import hashlib
    import hmac

    file_path = Path(path)
    data = file_path.read_bytes()
    sig = hmac.new(key, data, hashlib.sha256).hexdigest()
    sig_path = file_path.with_suffix(file_path.suffix + ".sig")
    sig_path.write_text(sig)
    logger.info("sign_file", extra={"file": str(file_path)})
    return sig_path


def upload_to_s3(
    path: Path | str,
    bucket: str,
    key: str,
    *,
    s3_client=None,
) -> None:
    """Upload ``path`` to S3 with basic object-lock protection.

    A custom ``s3_client`` can be injected for testing; otherwise a new client
    is created with ``boto3``.
    """
    if s3_client is None:
        import boto3

        s3_client = boto3.client("s3")

    with open(path, "rb") as f:
        s3_client.put_object(
            Bucket=bucket, Key=key, Body=f.read(), ObjectLockMode="COMPLIANCE"
        )
    logger.info("upload_to_s3", extra={"bucket": bucket, "key": key})
    

def create_bundle(files: list[Path | str]) -> Path:
    """Create a timestamped audit bundle containing ``files`` and metadata."""
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    bundle_path = Path(f"audit_bundle_{ts}.zip")
    with zipfile.ZipFile(bundle_path, "w") as zf:
        names: list[str] = []
        for f in files:
            f = Path(f)
            if f.exists():
                zf.write(f, arcname=f.name)
                names.append(f.name)
        meta = {"created": ts, "files": names}
        zf.writestr("metadata.json", json.dumps(meta))
    logger.info("create_bundle", extra={"file": str(bundle_path)})
    return bundle_path


def export() -> dict[str, str]:
    """Execute the report export workflow and return generated filenames."""
    logs = fetch_logs()

    # Determine next available version number
    version = 1
    while Path(f"logs_v{version}.csv").exists():
        version += 1

    csv_path = Path(f"logs_v{version}.csv")
    pdf_path = Path(f"logs_v{version}.pdf")

    generate_csv(logs, csv_path)
    generate_pdf(logs, pdf_path)
    csv_hash = hash_file(csv_path)
    pdf_hash = hash_file(pdf_path)

    sig_paths = []
    key = load_env("SIGNING_KEY", required=False)
    if key:
        key_bytes = key.encode()
        sig_paths.append(sign_file(csv_path, key_bytes))
        sig_paths.append(sign_file(pdf_path, key_bytes))

    bundle_files = [csv_path, pdf_path, csv_hash, pdf_hash] + sig_paths
    bundle_path = create_bundle(bundle_files)
    bundle_hash = hash_file(bundle_path)
    if key:
        sig_paths.append(sign_file(bundle_path, key_bytes))

    bucket = load_env("EXPORT_BUCKET", required=False)
    if bucket:
        upload_to_s3(csv_path, bucket, csv_path.name)
        upload_to_s3(pdf_path, bucket, pdf_path.name)
        upload_to_s3(bundle_path, bucket, bundle_path.name)
        upload_to_s3(bundle_hash, bucket, bundle_hash.name)
        for sig in sig_paths:
            upload_to_s3(sig, bucket, sig.name)

    return {
        "csv": csv_path.name,
        "pdf": pdf_path.name,
        "bundle": bundle_path.name,
    }



