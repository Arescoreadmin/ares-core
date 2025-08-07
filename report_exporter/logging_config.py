import logging
from datetime import datetime
import os
from pathlib import Path
import requests


def load_env(name: str, required: bool = True) -> str | None:
    """Fetch *name* from the environment or an associated secret file."""
    file_path = os.getenv(f"{name}_FILE")
    if file_path:
        return Path(file_path).read_text().strip()
    value = os.getenv(name)
    if value is None and required:
        raise RuntimeError(f"{name} is required")
    return value


LOG_INDEXER_URL = load_env("LOG_INDEXER_URL")


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
