import os
import logging
import json
from datetime import datetime
from pathlib import Path

import httpx
from fastapi import FastAPI

from .models import LogEvent, Alert

app = FastAPI(title="Behavior Analytics", version="0.1.0")

# Structured JSON logging
class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "service": "behavior_analytics",
            "message": record.getMessage(),
        }
        return json.dumps(data)

logger = logging.getLogger("behavior_analytics")
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.propagate = False

def read_env(name: str) -> str | None:
    value = os.getenv(name)
    if value:
        return value
    file_path = os.getenv(f"{name}_FILE")
    if file_path and Path(file_path).exists():
        return Path(file_path).read_text().strip()
    return None


ORCHESTRATOR_URL = read_env("ORCHESTRATOR_URL")
LOG_INDEXER_URL = read_env("LOG_INDEXER_URL")
LOG_INDEXER_TOKEN = read_env("LOG_INDEXER_TOKEN")


def log_to_indexer(level: str, message: str) -> None:
    if not LOG_INDEXER_URL:
        return
    payload = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": level,
        "service": "behavior_analytics",
        "message": message,
    }
    headers = {}
    if LOG_INDEXER_TOKEN:
        headers["Authorization"] = f"Bearer {LOG_INDEXER_TOKEN}"
    try:
        httpx.post(LOG_INDEXER_URL, json=payload, headers=headers, timeout=5)
    except Exception as exc:
        logger.error(f"failed to log to indexer: {exc}")


def send_alert(alert: Alert) -> None:
    if not ORCHESTRATOR_URL:
        return
    try:
        httpx.post(ORCHESTRATOR_URL, json=alert.model_dump(), timeout=5)
        log_to_indexer("INFO", "alert sent")
    except Exception as exc:
        logger.error(f"failed to send alert: {exc}")
        log_to_indexer("ERROR", f"alert send failure: {exc}")


def is_suspicious(event: LogEvent) -> bool:
    msg = event.message.lower()
    return "failed" in msg or event.level.upper() in {"ERROR", "CRITICAL"}


@app.get("/health")
def health():
    return {"status": "ok", "service": "behavior_analytics", "time": datetime.utcnow().isoformat()}


@app.post("/event")
def receive_event(event: LogEvent):
    suspicious = is_suspicious(event)
    if suspicious:
        alert = Alert(event=event, risk_score=0.9, summary="Suspicious event detected")
        send_alert(alert)
    log_to_indexer("INFO", f"processed event suspicious={suspicious}")
    return {"anomalous": suspicious}
