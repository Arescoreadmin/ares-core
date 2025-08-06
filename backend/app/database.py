from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from .config import get_database_url

# Optionally load a .env file for local development
load_dotenv()

# Read DB URL from environment or secret file
DATABASE_URL = get_database_url()

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Create a configured "SessionLocal" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency for FastAPI routes
def get_db():
    """Provide a database session to path operations."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
