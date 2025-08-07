import logging
from datetime import datetime
import os
from pathlib import Path
import requests


def load_env(name: str, required: bool = True) -> str | None:
    """Return the value of *name* from the environment or a mounted file.

    A ``*_FILE`` variant is checked first to support Docker secrets.  If the
    variable is marked as *required* and no value is found, ``RuntimeError`` is
    raised.
    """
    file_path = os.getenv(f"{name}_FILE")
    if file_path:
        return Path(file_path).read_text().strip()
    value = os.getenv(name)
    if value is None and required:
        raise RuntimeError(f"{name} is required")
    return value


LOG_INDEXER_URL = load_env("LOG_INDEXER_URL")


class LogIndexerHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "service": "sentinelcore-ai",
            "message": record.getMessage(),
        }
        try:
            requests.post(f"{LOG_INDEXER_URL}/log", json=log_entry, timeout=2)
        except Exception:
            # Avoid crashing on logging errors
            pass


def setup_logging() -> logging.Logger:
    """Configure logger for sentinelcore-ai service."""
    logger = logging.getLogger("sentinelcore-ai")
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = LogIndexerHandler()
        logger.addHandler(handler)
    return logger
