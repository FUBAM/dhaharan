from app.core.database import SessionLocal
from app.core.security import hash_password
from app.modules.users.models import User


def run():
    db = SessionLocal()

    existing = db.query(User).filter(
        User.email == "demo@dhaharan.com"
    ).first()

    if existing:
        print("Demo user already exists.")
        db.close()
        return

    user = User(
        name="Demo User",
        email="demo@dhaharan.com",
        password_hash=hash_password("password123"),
        country="Indonesia",
        province="Jawa Barat",
        city="Bandung",
        is_active=True
    )

    db.add(user)
    db.commit()
    db.close()

    print("Demo user created.")
    print("email: demo@dhaharan.com")
    print("password: password123")


if __name__ == "__main__":
    run()