from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class LogEntry(BaseModel):
    timestamp: datetime
    level: str
    service: str
    message: str
    hash: Optional[str] = None
