from __future__ import annotations

from pathlib import Path
from typing import List, Optional
import sqlite3
from datetime import datetime

from .models import LogEntry

class LogDAO:
    """Data access object for log entries backed by SQLite."""

    def __init__(self, db_path: Path):
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._setup()

    def _setup(self) -> None:
        with self._conn:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    level TEXT NOT NULL,
                    service TEXT NOT NULL,
                    message TEXT NOT NULL,
                    hash TEXT NOT NULL
                )
                """
            )

    def add_log(self, entry: LogEntry) -> None:
        with self._conn:
            self._conn.execute(
                "INSERT INTO logs (timestamp, level, service, message, hash) VALUES (?, ?, ?, ?, ?)",
                (
                    entry.timestamp.isoformat(),
                    entry.level,
                    entry.service,
                    entry.message,
                    entry.hash,
                ),
            )

    def query_logs(self, level: Optional[str] = None, service: Optional[str] = None) -> List[LogEntry]:
        query = "SELECT timestamp, level, service, message, hash FROM logs"
        conditions = []
        params: List[str] = []
        if level:
            conditions.append("level = ?")
            params.append(level)
        if service:
            conditions.append("service = ?")
            params.append(service)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        cursor = self._conn.execute(query, params)
        rows = cursor.fetchall()
        return [
            LogEntry(
                timestamp=datetime.fromisoformat(row["timestamp"]),
                level=row["level"],
                service=row["service"],
                message=row["message"],
                hash=row["hash"],
            )
            for row in rows
        ]

    def all_logs(self) -> List[LogEntry]:
        return self.query_logs()
