from fastapi import FastAPI
from logging_config import setup_logging

app = FastAPI()
logger = setup_logging()


@app.post("/incident")
async def create_incident(incident: dict):
    """Receive an incident payload."""
    logger.info("create_incident")
    return {"received": incident}


@app.get("/health")
async def health():
    """Health check endpoint."""
    logger.info("health_check")
    return {"status": "ok"}
