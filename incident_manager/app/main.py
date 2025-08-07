from fastapi import FastAPI, Request
from incident_manager.logging_config import setup_logging

logger = setup_logging()
app = FastAPI()

@app.get("/")
async def root():
    return {"service": "incident_manager"}


@app.get("/health")
async def health(request: Request):
    logger.info("Health check request at %s", request.url.path)
    return {"status": "ok"}
