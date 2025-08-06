from sqlalchemy.orm import Session
import bcrypt
from . import models, schemas

def get_users(db: Session):
    return db.query(models.User).all()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed = bcrypt.hashpw(user.hashed_password.encode(), bcrypt.gensalt())
    db_user = models.User(email=user.email, hashed_password=hashed.decode())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
