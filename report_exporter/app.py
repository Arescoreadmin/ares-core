from fastapi import FastAPI

from .exporter import export

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/export")
def export_endpoint():
    return export()

