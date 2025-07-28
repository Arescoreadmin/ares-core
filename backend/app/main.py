from fastapi import FastAPI

app = FastAPI(title="AresCore API", version="0.1")

@app.get("/")
def root():
    return {"status": "AresCore backend running"}

