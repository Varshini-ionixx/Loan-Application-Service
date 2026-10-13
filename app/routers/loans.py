from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user, require_officer
from app.database import get_db
from app.models import Loan, User
from app.schemas import LoanCreate, LoanResponse, LoanUpdate
from app.services.loan_service import (
    apply_loan,
    edit_loan,
    get_loan,
    get_loans,
    remove_loan,
)

router = APIRouter(prefix="/loans", tags=["Loans"])


@router.post(
    "/",
    response_model=LoanResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_loan(
    loan: LoanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == "CUSTOMER":
        if current_user.customer_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account is not linked to a customer record",
            )

        if loan.customer_id != current_user.customer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can apply for loans only for your own customer account",
            )

    elif current_user.role != "OFFICER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    return apply_loan(db, loan)


@router.get("/", response_model=list[LoanResponse])
def read_loans(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == "OFFICER":
        return get_loans(db)

    if current_user.role == "CUSTOMER":
        if current_user.customer_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account is not linked to a customer record",
            )

        return db.query(Loan).filter(Loan.customer_id == current_user.customer_id).all()

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Insufficient permissions",
    )


@router.get("/{loan_id}", response_model=LoanResponse)
def read_loan(
    loan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    loan = get_loan(db, loan_id)

    if current_user.role == "OFFICER":
        return loan

    if current_user.role == "CUSTOMER":
        if current_user.customer_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account is not linked to a customer record",
            )

        if loan.customer_id != current_user.customer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot access another customer's loan",
            )

        return loan

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Insufficient permissions",
    )


@router.put("/{loan_id}", response_model=LoanResponse)
def update_loan(
    loan_id: int,
    loan: LoanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_officer),
):
    return edit_loan(db, loan_id, loan)


@router.patch("/{loan_id}", response_model=LoanResponse)
def patch_loan(
    loan_id: int,
    loan: LoanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_officer),
):
    return edit_loan(db, loan_id, loan)


@router.delete("/{loan_id}")
def delete_loan(
    loan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_officer),
):
    return remove_loan(db, loan_id)
