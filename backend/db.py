from app.database import SessionLocal
from app.models import User

def main():
    db = SessionLocal()

    # Query all users
    users = db.query(User).all()
    print("Users in DB:")
    for u in users:
        print(f"- {u.id}: {u.email}")

    # Insert a test user (if not exists)
    if not any(u.email == "devtest@example.com" for u in users):
        new_user = User(email="devtest@example.com", hashed_password="test123")
        db.add(new_user)
        db.commit()
        print("Inserted devtest@example.com")
    else:
        print("devtest@example.com already exists")

    db.close()

if __name__ == "__main__":
    main()
