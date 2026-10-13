from getpass import getpass

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Customer, User
from app.security import hash_password


def main() -> None:
    email = input("Test user email: ").strip().lower()
    password = getpass("Test user password: ")
    customer_id_input = input("Existing customer ID: ").strip()

    if not email or len(password) < 12:
        raise SystemExit("Provide an email and a password of at least 12 characters.")

    try:
        customer_id = int(customer_id_input)
    except ValueError as exc:
        raise SystemExit("Customer ID must be a valid integer.") from exc

    db: Session = SessionLocal()

    try:
        existing_user = db.query(User).filter(User.email == email).first()

        if existing_user:
            print("A user with that email already exists. No changes made.")
            return

        customer = db.query(Customer).filter(Customer.id == customer_id).first()

        if customer is None:
            raise SystemExit(f"Customer ID {customer_id} does not exist.")

        linked_user = db.query(User).filter(User.customer_id == customer_id).first()

        if linked_user:
            raise SystemExit("That customer is already linked to a user account.")

        user = User(
            email=email,
            hashed_password=hash_password(password),
            role="CUSTOMER",
            customer_id=customer_id,
        )

        db.add(user)
        db.commit()

        print(f"Created CUSTOMER test account: {email}")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
