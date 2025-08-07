from fastapi import FastAPI, Request
from incident_manager.logging_config import setup_logging

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
