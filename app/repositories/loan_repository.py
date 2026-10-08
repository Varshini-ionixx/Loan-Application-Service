from sqlalchemy.orm import Session
 
from app.models import Loan
 
 
 
def create_loan(
    db: Session,
    loan: Loan
):
 
    db.add(loan)
    db.commit()
    db.refresh(loan)
 
    return loan
 
 
 
def get_loan_by_id(
    db: Session,
    loan_id: int
):
 
    return db.query(Loan).filter(
        Loan.id == loan_id
    ).first()
 
 
 
def get_all_loans(
    db: Session
):
 
    return db.query(Loan).all()
 
 
 
def update_loan(
    db: Session,
    loan: Loan,
    update_data: dict
):
 
    for key, value in update_data.items():
        setattr(loan, key, value)
 
    db.commit()
    db.refresh(loan)
 
    return loan
 
 
 
def delete_loan(
    db: Session,
    loan: Loan
):
 
    db.delete(loan)
    db.commit()