from fastapi import FastAPI, HTTPException
import httpx
import asyncio
from logging_config import setup_logging, load_env

app = FastAPI()
logger = setup_logging()

INCIDENT_MANAGER_URL = load_env("INCIDENT_MANAGER_URL")


@app.post("/analyze")
async def analyze(payload: dict):
    """Analyze a payload and forward it to the incident manager."""
    logger.info("analyze")
    for attempt in range(3):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{INCIDENT_MANAGER_URL}/incident", json=payload, timeout=5
                )
            if response.status_code == 200:
                return {"status": "processed"}
            logger.error(
                "incident_manager_error",
                extra={"status_code": response.status_code, "attempt": attempt + 1},
            )
        except Exception as exc:
            logger.error("incident_manager_exception", extra={"error": str(exc), "attempt": attempt + 1})
        await asyncio.sleep(2 ** attempt)
    raise HTTPException(status_code=500, detail="Incident manager error")


@app.get("/health")
async def health():
    """Health check endpoint."""
    logger.info("health_check")
    return {"status": "ok"}
