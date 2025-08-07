import os
from fastapi import FastAPI, Response, Header, HTTPException
from typing import List, Optional
from datetime import datetime
import logging
import json
from io import StringIO
import csv
import hashlib
from pathlib import Path

from .models import LogEntry
from .dao import LogDAO

app = FastAPI(title="Log Indexer", version="0.1.0")

# Structured console logging for this service
class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "service": "log_indexer",
            "message": record.getMessage(),
        }
        return json.dumps(log_entry)

logger = logging.getLogger("log_indexer")
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.propagate = False

dao = LogDAO(Path(__file__).resolve().parent / "logs.db")
API_TOKEN = os.getenv("LOG_INDEXER_TOKEN")

@app.get("/health")
def health():
    """Basic health check endpoint."""
    return {"status": "ok", "service": "log_indexer", "time": datetime.utcnow().isoformat()}

@app.post("/log", status_code=201)
def ingest_log(entry: LogEntry, authorization: str | None = Header(default=None)):
    """Receive a log entry and store it.

    If ``LOG_INDEXER_TOKEN`` is set, the request must include an
    ``Authorization`` header with ``Bearer <token>``.
    """
    if API_TOKEN:
        if authorization != f"Bearer {API_TOKEN}":
            raise HTTPException(status_code=401, detail="Unauthorized")
    payload = f"{entry.timestamp.isoformat()}|{entry.level}|{entry.service}|{entry.message}"
    entry.hash = hashlib.sha256(payload.encode()).hexdigest()
    dao.add_log(entry)
    logger.info("log received", extra={"source": entry.service})
    return {"status": "ok"}

@app.get("/query", response_model=List[LogEntry])
def query_logs(level: Optional[str] = None, service: Optional[str] = None):
    """Query stored logs with optional filters."""
    return dao.query_logs(level=level, service=service)

@app.get("/export")
def export_logs(format: str = "json"):
    """Export logs as JSON or CSV."""
    logs = dao.all_logs()
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    export_dir = Path(__file__).resolve().parent / "export"
    export_dir.mkdir(exist_ok=True)

    if format == "csv":
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["timestamp", "level", "service", "message", "hash"])
        for log in logs:
            writer.writerow([
                log.timestamp.isoformat(),
                log.level,
                log.service,
                log.message,
                log.hash,
            ])
        data = output.getvalue()
        file_path = export_dir / f"logs_{timestamp}.csv"
        file_path.write_text(data)
        hash_value = hashlib.sha256(data.encode()).hexdigest()
        meta = {"version": timestamp, "algorithm": "SHA256", "hash": hash_value}
        (export_dir / f"logs_{timestamp}.metadata.json").write_text(json.dumps(meta))
        return Response(content=data, media_type="text/csv", headers={"X-Export-Version": timestamp, "X-Integrity-Hash": hash_value})

    logs_data = [log.dict() for log in logs]
    data = json.dumps(logs_data)
    file_path = export_dir / f"logs_{timestamp}.json"
    file_path.write_text(data)
    hash_value = hashlib.sha256(data.encode()).hexdigest()
    meta = {"version": timestamp, "algorithm": "SHA256", "hash": hash_value}
    (export_dir / f"logs_{timestamp}.metadata.json").write_text(json.dumps(meta))
    return {"version": timestamp, "integrity": meta, "logs": logs_data}
