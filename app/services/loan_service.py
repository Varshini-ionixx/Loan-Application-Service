from fastapi import HTTPException
from sqlalchemy.orm import Session
 
from app.models import Loan
 
from app.schemas import (
    LoanCreate,
    LoanUpdate
)
 
from app.repositories.loan_repository import (
    create_loan,
    get_loan_by_id,
    get_all_loans,
    update_loan,
    delete_loan
)
 
from app.repositories.customer_repository import (
    get_customer_by_id
)
 
 
 
def calculate_emi(
    amount: float,
    rate: float,
    tenure: int
):
 
    monthly_rate = rate / (12 * 100)
 
    emi = (
        amount
        * monthly_rate
        * (1 + monthly_rate) ** tenure
    ) / (
        ((1 + monthly_rate) ** tenure) - 1
    )
 
    return round(emi, 2)
 
 
 
def apply_loan(
    db: Session,
    loan_data: LoanCreate
):
 
    customer = get_customer_by_id(
        db,
        loan_data.customer_id
    )
 
 
    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )
 
 
    rate_map = {
        12: 10,
        24: 11,
        36: 12,
        48: 13,
        60: 13
    }
 
 
    rate = rate_map.get(
        loan_data.tenure_months
    )
 
 
    if rate is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid tenure"
        )
 
 
    emi = calculate_emi(
        loan_data.amount,
        rate,
        loan_data.tenure_months
    )
 
 
    loan = Loan(
        customer_id=loan_data.customer_id,
        amount=loan_data.amount,
        tenure_months=loan_data.tenure_months,
        interest_rate=rate,
        monthly_emi=emi,
        status="APPROVED"
    )
 
 
    return create_loan(
        db,
        loan
    )
 
 
 
def get_loan(
    db: Session,
    loan_id: int
):
 
    loan = get_loan_by_id(
        db,
        loan_id
    )
 
 
    if not loan:
        raise HTTPException(
            status_code=404,
            detail="Loan not found"
        )
 
 
    return loan
 
 
 
def get_loans(
    db: Session
):
 
    return get_all_loans(db)
 
 
 
def edit_loan(
    db: Session,
    loan_id: int,
    loan_data: LoanUpdate
):
 
    loan = get_loan_by_id(
        db,
        loan_id
    )
 
 
    if not loan:
        raise HTTPException(
            status_code=404,
            detail="Loan not found"
        )
 
 
    data = loan_data.model_dump(
        exclude_unset=True
    )
 
 
    return update_loan(
        db,
        loan,
        data
    )
 
 
 
def remove_loan(
    db: Session,
    loan_id: int
):
 
    loan = get_loan_by_id(
        db,
        loan_id
    )
 
 
    if not loan:
        raise HTTPException(
            status_code=404,
            detail="Loan not found"
        )
 
 
    delete_loan(
        db,
        loan
    )
 
 
    return {
        "message": "Loan deleted successfully"
    }
 