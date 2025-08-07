import os
import csv
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
        writer = csv.DictWriter(f, fieldnames=["message", "level"])
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
    import hmac
    import hashlib
    data = path.read_bytes()
    sig = hmac.new(key, data, hashlib.sha256).hexdigest()
    sig_path = path.with_suffix(path.suffix + ".sig")
    sig_path.write_text(sig)
    logger.info("sign_file", extra={"file": str(path)})
    return sig_path


def upload_to_s3(path, bucket, key, s3_client=None):
    """Upload a file to S3 with basic object lock settings."""
    if s3_client is None:
        import boto3
        s3_client = boto3.client("s3")
    with open(path, "rb") as f:
        s3_client.put_object(Bucket=bucket, Key=key, Body=f.read(), ObjectLockMode="COMPLIANCE")
    logger.info("upload_to_s3", extra={"bucket": bucket, "key": key})


def main():
    logs = fetch_logs()
    generate_csv(logs, "logs.csv")
    generate_pdf(logs, "logs.pdf")


if __name__ == "__main__":
    main()
