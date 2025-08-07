import logging
from datetime import datetime
import os
from pathlib import Path
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


def load_env(name: str, required: bool = True) -> str | None:
    """Fetch *name* from the environment or an associated secret file."""
    file_path = os.getenv(f"{name}_FILE")
    if file_path:
        return Path(file_path).read_text().strip()
    value = os.getenv(name)
    if value is None and required:
        raise RuntimeError(f"{name} is required")
    return value


LOG_INDEXER_URL = load_env("LOG_INDEXER_URL", required=False)

_session = requests.Session()
_adapter = HTTPAdapter(max_retries=Retry(total=3, backoff_factor=0.5))
_session.mount("http://", _adapter)
_session.mount("https://", _adapter)

SERVICE_NAME = "__SERVICE_NAME__"


class LogIndexerHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        if not LOG_INDEXER_URL:
            return
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "service": SERVICE_NAME,
            "message": record.getMessage(),
        }
        try:
            _session.post(f"{LOG_INDEXER_URL}/log", json=log_entry, timeout=5)
        except Exception:
            # Avoid crashing on logging errors
            pass


def setup_logging() -> logging.Logger:
    """Configure and return a logger for the service."""
    logger = logging.getLogger(SERVICE_NAME)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        logger.addHandler(LogIndexerHandler())
    return logger
