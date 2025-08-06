from fastapi import FastAPI

app = FastAPI(title="AresCore API Gateway", version="0.1.0")


@app.get("/health")
def health_check():
    """Basic health check for the gateway service."""
    return {"status": "ok"}
