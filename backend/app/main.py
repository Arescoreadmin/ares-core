from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app import models, schemas, crud
from app.database import engine, get_db
from app.logging_config import setup_logging

# Auto-create tables at startup (solo dev convenience)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AresCore API", version="0.1.0")
logger = setup_logging()

# --- ROUTES ---

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/users", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user.
    """
    logger.info("create_user", extra={"email": user.email})
    return crud.create_user(db=db, user=user)

@app.get("/users", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Fetch a list of users with optional pagination.
    """
    logger.info("read_users", extra={"skip": skip, "limit": limit})
    return crud.get_users(db=db, skip=skip, limit=limit)
