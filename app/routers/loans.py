from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth import get_current_user, require_officer
from app.database import get_db
from app.models import User
from app.schemas import (
    LoanCreate,
    LoanPageResponse,
    LoanResponse,
    LoanUpdate,
)
from app.services.loan_service import (
    apply_loan,
    edit_loan,
    get_loan,
    get_loans,
    remove_loan,
)

router = APIRouter(prefix="/loans", tags=["Loans"])


def ensure_customer_linked(user: User) -> int:
    """Return the linked customer ID or reject an unlinked customer."""
    if user.customer_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is not linked to a customer record",
        )

    return user.customer_id


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
    """Customers can apply only for themselves; officers can apply for any customer."""
    if current_user.role == "CUSTOMER":
        customer_id = ensure_customer_linked(current_user)

        if loan.customer_id != customer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can apply for loans only for your own customer account",
            )

    elif current_user.role != "OFFICER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to apply for loans",
        )

    return apply_loan(db, loan)


@router.get("/", response_model=LoanPageResponse)
def read_loans(
    status_filter: str | None = Query(default=None, alias="status", max_length=20),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Officers see all loans; customers see only their own loans."""
    if current_user.role == "OFFICER":
        customer_id = None
    elif current_user.role == "CUSTOMER":
        customer_id = ensure_customer_linked(current_user)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view loans",
        )

    status_filter = status_filter.strip() if status_filter else None
    status_filter = status_filter or None

    return get_loans(
        db,
        status_filter=status_filter,
        customer_id=customer_id,
        page=page,
        size=size,
    )


@router.get("/{loan_id}", response_model=LoanResponse)
def read_loan(
    loan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Customers can view only their own loans; officers can view any loan."""
    loan = get_loan(db, loan_id)

    if current_user.role == "OFFICER":
        return loan

    if current_user.role == "CUSTOMER":
        customer_id = ensure_customer_linked(current_user)

        if loan.customer_id != customer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to view this loan",
            )

        return loan

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to view loans",
    )


@router.put("/{loan_id}", response_model=LoanResponse)
def update_loan(
    loan_id: int,
    loan: LoanUpdate,
    db: Session = Depends(get_db),
    officer: User = Depends(require_officer),
):
    """Only officers can replace loan details."""
    return edit_loan(db, loan_id, loan)


@router.patch("/{loan_id}", response_model=LoanResponse)
def partially_update_loan(
    loan_id: int,
    loan: LoanUpdate,
    db: Session = Depends(get_db),
    officer: User = Depends(require_officer),
):
    """Only officers can update loan details."""
    return edit_loan(db, loan_id, loan)


@router.delete("/{loan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_loan(
    loan_id: int,
    db: Session = Depends(get_db),
    officer: User = Depends(require_officer),
):
    """Only officers can delete loans."""
    remove_loan(db, loan_id)
