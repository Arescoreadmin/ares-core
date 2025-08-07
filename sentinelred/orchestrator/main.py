from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/modules")
def list_modules():
    return {"modules": []}

@app.get("/logs")
def get_logs():
    return {"logs": []}
