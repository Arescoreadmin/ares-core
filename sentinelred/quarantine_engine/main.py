from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

quarantined_items = set()

class Item(BaseModel):
    item: str

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/quarantine")
def quarantine_item(payload: Item):
    quarantined_items.add(payload.item)
    return {"status": "quarantined", "item": payload.item}

@app.post("/restore")
def restore_item(payload: Item):
    if payload.item not in quarantined_items:
        raise HTTPException(status_code=404, detail="Item not found")
    quarantined_items.remove(payload.item)
    return {"status": "restored", "item": payload.item}
