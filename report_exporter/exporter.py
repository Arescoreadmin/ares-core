import os
import csv
from pathlib import Path

import requests
from fpdf import FPDF

from .logging_config import setup_logging

LOG_INDEXER_URL = os.getenv("LOG_INDEXER_URL", "http://localhost:8001")
logger = setup_logging("report_exporter")


def fetch_logs():
    logger.info("fetch_logs")
    resp = requests.get(f"{LOG_INDEXER_URL}/export")
    resp.raise_for_status()
    return resp.json()


def generate_csv(logs, filename):
    """Write logs to a CSV file."""
    logger.info("generate_csv", extra={"file": str(filename)})
    with open(filename, "w", newline="") as f:
        # Explicitly use Unix newlines so tests get predictable output
        writer = csv.DictWriter(
            f, fieldnames=["message", "level"], lineterminator="\n"
        )
        writer.writeheader()
        for log in logs:
            writer.writerow({"message": log.get("message"), "level": log.get("level")})

def generate_pdf(logs, filename):
    """Write logs to a PDF file."""
    logger.info("generate_pdf", extra={"file": str(filename)})
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for log in logs:
        line = f"{log['timestamp']} {log['level']} {log['service']} {log['message']}"
        pdf.multi_cell(0, 10, line)
    pdf.output(filename)


def sign_file(path, key):
    """Generate an HMAC-SHA256 signature for a file."""
    import hashlib
    import hmac

    file_path = Path(path)
    data = file_path.read_bytes()
    sig = hmac.new(key, data, hashlib.sha256).hexdigest()
    sig_path = file_path.with_suffix(file_path.suffix + ".sig")
    sig_path.write_text(sig)
    logger.info("sign_file", extra={"file": str(file_path)})
    return sig_path


def upload_to_s3(path, bucket, key, s3_client=None):
    """Upload a file to S3 with basic object lock settings."""
    if s3_client is None:
        import boto3

        s3_client = boto3.client("s3")

    with open(path, "rb") as f:
        s3_client.put_object(
            Bucket=bucket, Key=key, Body=f.read(), ObjectLockMode="COMPLIANCE"
        )
    logger.info("upload_to_s3", extra={"bucket": bucket, "key": key})


def main():
    logs = fetch_logs()

    # Determine next available version number
    version = 1
    while Path(f"logs_v{version}.csv").exists():
        version += 1

    csv_path = Path(f"logs_v{version}.csv")
    pdf_path = Path(f"logs_v{version}.pdf")

    generate_csv(logs, csv_path)
    generate_pdf(logs, pdf_path)

    sig_paths = []
    key = os.getenv("SIGNING_KEY")
    if key:
        key_bytes = key.encode()
        sig_paths.append(sign_file(csv_path, key_bytes))
        sig_paths.append(sign_file(pdf_path, key_bytes))

    bucket = os.getenv("EXPORT_BUCKET")
    if bucket:
        upload_to_s3(csv_path, bucket, csv_path.name)
        upload_to_s3(pdf_path, bucket, pdf_path.name)
        for sig in sig_paths:
            upload_to_s3(sig, bucket, sig.name)


if __name__ == "__main__":
    main()
