import os

import bcrypt

from app.database import SessionLocal
from app.models import User

def main():
    db = SessionLocal()

    # Query all users
    users = db.query(User).all()
    print("Users in DB:")
    for u in users:
        print(f"- {u.id}: {u.email}")

    # Seed a user from environment variables, if provided
    seed_email = os.getenv("SEED_USER_EMAIL")
    seed_password = os.getenv("SEED_USER_PASSWORD")

    if seed_email and seed_password:
        if not any(u.email == seed_email for u in users):
            hashed = bcrypt.hashpw(
                seed_password.encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")
            new_user = User(email=seed_email, hashed_password=hashed)
            db.add(new_user)
            db.commit()
            print(f"Inserted {seed_email}")
        else:
            print(f"{seed_email} already exists")
    else:
        print("No seed user credentials provided in environment variables.")

    db.close()

if __name__ == "__main__":
    main()
