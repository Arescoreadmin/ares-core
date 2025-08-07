from fastapi import FastAPI, HTTPException
import httpx
import os
from logging_config import setup_logging

app = FastAPI()
logger = setup_logging()

INCIDENT_MANAGER_URL = os.getenv("INCIDENT_MANAGER_URL", "http://incident_manager:8001")


@app.post("/analyze")
async def analyze(payload: dict):
    """Analyze a payload and forward it to the incident manager."""
    logger.info("analyze")
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{INCIDENT_MANAGER_URL}/incident", json=payload)
    if response.status_code != 200:
        logger.error("incident_manager_error", extra={"status_code": response.status_code})
        raise HTTPException(status_code=500, detail="Incident manager error")
    return {"status": "processed"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    logger.info("health_check")
    return {"status": "ok"}
