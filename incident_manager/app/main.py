from fastapi import FastAPI, Request
from incident_manager.logging_config import setup_logging
from typing import Dict, Any

logger = setup_logging()
app = FastAPI()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info("Request: %s %s", request.method, request.url.path)
    response = await call_next(request)
    logger.info(
        "Response: %s %s -> %d", request.method, request.url.path, response.status_code
    )
    return response


@app.get("/")
async def root():
    return {"service": "incident_manager"}


@app.get("/health")
async def health(request: Request):
    logger.info("Health check request at %s", request.url.path)
    return {"status": "ok"}


@app.post("/incident")
async def create_incident(payload: Dict[str, Any]):
    """Accept a new incident report and log the event."""
    logger.info("incident_created", extra={"payload": payload})
    return {"status": "received"}
