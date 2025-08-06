import os
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8000")

app = FastAPI(title="Incident Manager", version="0.1.0")


class Incident(BaseModel):
    user_id: int
    description: str


@app.post("/incident")
def create_incident(incident: Incident):
    """Record an incident for a user by calling the user service."""
    response = requests.get(f"{USER_SERVICE_URL}/users/{incident.user_id}")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="User not found")
    user = response.json()
    return {"status": "incident recorded", "user": user, "description": incident.description}
