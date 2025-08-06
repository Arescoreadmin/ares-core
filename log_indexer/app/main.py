from fastapi import FastAPI, Response
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import logging
import json
from io import StringIO
import csv

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


class LogEntry(BaseModel):
    timestamp: datetime
    level: str
    service: str
    message: str


LOGS: List[LogEntry] = []


@app.post("/log", status_code=201)
def ingest_log(entry: LogEntry):
    """Receive a log entry and store it."""
    LOGS.append(entry)
    logger.info("log received", extra={"source": entry.service})
    return {"status": "ok"}


@app.get("/query", response_model=List[LogEntry])
def query_logs(level: Optional[str] = None, service: Optional[str] = None):
    """Query stored logs with optional filters."""
    result = LOGS
    if level:
        result = [log for log in result if log.level == level]
    if service:
        result = [log for log in result if log.service == service]
    return result


@app.get("/export")
def export_logs(format: str = "json"):
    """Export logs as JSON or CSV."""
    if format == "csv":
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["timestamp", "level", "service", "message"])
        for log in LOGS:
            writer.writerow([
                log.timestamp.isoformat(),
                log.level,
                log.service,
                log.message,
            ])
        return Response(content=output.getvalue(), media_type="text/csv")
    return [log.dict() for log in LOGS]
