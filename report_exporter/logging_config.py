import logging
from datetime import datetime
import os
import requests

LOG_INDEXER_URL = os.getenv("LOG_INDEXER_URL", "http://localhost:8001")


class LogIndexerHandler(logging.Handler):
    def __init__(self, service_name: str):
        super().__init__()
        self.service_name = service_name

    def emit(self, record: logging.LogRecord) -> None:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "service": self.service_name,
            "message": record.getMessage(),
        }
        try:
            requests.post(f"{LOG_INDEXER_URL}/log", json=log_entry, timeout=2)
        except Exception:
            pass


def setup_logging(service_name: str) -> logging.Logger:
    logger = logging.getLogger(service_name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = LogIndexerHandler(service_name)
        logger.addHandler(handler)
    return logger
