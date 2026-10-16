from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Loan


def create_loan(db: Session, loan: Loan):
    db.add(loan)
    return loan


def get_loan_by_id(db: Session, loan_id: int):
    return db.query(Loan).filter(Loan.id == loan_id).first()


def get_all_loans(
    db: Session,
    status_filter: str | None = None,
    customer_id: int | None = None,
    page: int = 1,
    size: int = 10,
):
    query = db.query(Loan)

    if status_filter:
        query = query.filter(func.upper(Loan.status) == status_filter.upper())

    if customer_id is not None:
        query = query.filter(Loan.customer_id == customer_id)

    total = query.count()

    loans = query.order_by(Loan.id).offset((page - 1) * size).limit(size).all()

    return loans, total


def update_loan(db: Session, loan: Loan, update_data: dict):
    for key, value in update_data.items():
        setattr(loan, key, value)

    return loan


def delete_loan(db: Session, loan: Loan):
    db.delete(loan)
