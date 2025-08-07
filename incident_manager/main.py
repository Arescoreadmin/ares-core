from fastapi import FastAPI

app = FastAPI()

@app.post("/incident")
async def create_incident(incident: dict):
    return {"received": incident}


@app.get("/health")
async def health():
    return {"status": "ok"}
