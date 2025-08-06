import os
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8000")

app = FastAPI(title="Notification Dispatcher", version="0.1.0")


class Notification(BaseModel):
    user_id: int
    message: str


@app.post("/notify")
def send_notification(notification: Notification):
    """Send a notification to a user after fetching details from the user service."""
    response = requests.get(f"{USER_SERVICE_URL}/users/{notification.user_id}")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="User not found")
    user = response.json()
    return {"status": f"notification sent to {user['email']}", "message": notification.message}
