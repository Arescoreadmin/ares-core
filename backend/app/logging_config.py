import logging
from datetime import datetime
import os
import requests

LOG_INDEXER_URL = os.getenv("LOG_INDEXER_URL", "http://localhost:8001")


class LogIndexerHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "service": "backend",
            "message": record.getMessage(),
        }
        try:
            requests.post(f"{LOG_INDEXER_URL}/log", json=log_entry, timeout=2)
        except Exception:
            # Avoid crashing on logging errors
            pass


def setup_logging() -> logging.Logger:
    """Configure logger for backend service."""
    logger = logging.getLogger("backend")
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = LogIndexerHandler()
        logger.addHandler(handler)
    return logger
