from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
 
from app.database import get_db
 
from app.schemas import (
    LoanCreate,
    LoanUpdate,
    LoanResponse
)
 
from app.services.loan_service import (
    apply_loan,
    get_loan,
    get_loans,
    edit_loan,
    remove_loan
)
 
 
 
router = APIRouter(
    prefix="/loans",
    tags=["Loans"]
)
 
 
 
@router.post(
    "/",
    response_model=LoanResponse,
    status_code=status.HTTP_201_CREATED
)
def create_loan(
    loan: LoanCreate,
    db: Session = Depends(get_db)
):
 
    return apply_loan(
        db,
        loan
    )
 
 
 
@router.get(
    "/",
    response_model=list[LoanResponse]
)
def read_loans(
    db: Session = Depends(get_db)
):
 
    return get_loans(db)
 
 
 
@router.get(
    "/{loan_id}",
    response_model=LoanResponse
)
def read_loan(
    loan_id: int,
    db: Session = Depends(get_db)
):
 
    return get_loan(
        db,
        loan_id
    )
 
 
 
@router.put(
    "/{loan_id}",
    response_model=LoanResponse
)
def update_loan(
    loan_id: int,
    loan: LoanUpdate,
    db: Session = Depends(get_db)
):
 
    return edit_loan(
        db,
        loan_id,
        loan
    )
 
 
 
@router.patch(
    "/{loan_id}",
    response_model=LoanResponse
)
def patch_loan(
    loan_id: int,
    loan: LoanUpdate,
    db: Session = Depends(get_db)
):
 
    return edit_loan(
        db,
        loan_id,
        loan
    )
 
 
 
@router.delete(
    "/{loan_id}"
)
def delete_loan(
    loan_id: int,
    db: Session = Depends(get_db)
):
 
    return remove_loan(
        db,
        loan_id
    )
 