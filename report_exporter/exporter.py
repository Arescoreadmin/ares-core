import os
import csv
import requests
from fpdf import FPDF
from logging_config import setup_logging

LOG_INDEXER_URL = os.getenv("LOG_INDEXER_URL", "http://localhost:8001")
logger = setup_logging("report_exporter")


def fetch_logs():
    logger.info("fetch_logs")
    resp = requests.get(f"{LOG_INDEXER_URL}/export")
    resp.raise_for_status()
    return resp.json()


def export_csv(logs, filename):
    logger.info("export_csv", extra={"filename": filename})
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "level", "service", "message"])
        writer.writeheader()
        for log in logs:
            writer.writerow(log)


def export_pdf(logs, filename):
    logger.info("export_pdf", extra={"filename": filename})
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for log in logs:
        line = f"{log['timestamp']} {log['level']} {log['service']} {log['message']}"
        pdf.multi_cell(0, 10, line)
    pdf.output(filename)


def main():
    logs = fetch_logs()
    export_csv(logs, "logs.csv")
    export_pdf(logs, "logs.pdf")


if __name__ == "__main__":
    main()
