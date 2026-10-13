from getpass import getpass

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import User
from app.security import hash_password


def main() -> None:
    email = input("Officer email: ").strip().lower()
    password = getpass("Officer password: ")

    if not email or len(password) < 12:
        raise SystemExit("Provide an email and a password of at least 12 characters.")

    db: Session = SessionLocal()

    try:
        existing_user = db.query(User).filter(User.email == email).first()

        if existing_user:
            print("A user with that email already exists. No changes made.")
            return

        officer = User(
            email=email,
            hashed_password=hash_password(password),
            role="OFFICER",
            customer_id=None,
        )

        db.add(officer)
        db.commit()

        print(f"Created OFFICER test account: {email}")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
