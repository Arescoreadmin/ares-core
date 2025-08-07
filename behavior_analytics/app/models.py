from datetime import datetime
from pydantic import BaseModel, Field

class LogEvent(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    level: str
    service: str
    message: str

class Alert(BaseModel):
    event: LogEvent
    risk_score: float
    summary: str
