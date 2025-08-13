from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.logging_config import load_env

SQLALCHEMY_DATABASE_URL = load_env("DATABASE_URL", required=True)

engine_kwargs = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(SQLALCHEMY_DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
