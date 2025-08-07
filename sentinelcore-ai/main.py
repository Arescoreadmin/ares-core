from fastapi import FastAPI, HTTPException
import httpx
import os

app = FastAPI()

INCIDENT_MANAGER_URL = os.getenv("INCIDENT_MANAGER_URL", "http://incident_manager:8001")

@app.post("/analyze")
async def analyze(payload: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{INCIDENT_MANAGER_URL}/incident", json=payload)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Incident manager error")
    return {"status": "processed"}


@app.get("/health")
async def health():
    return {"status": "ok"}
