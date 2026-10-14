from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user, require_officer
from app.database import get_db
from app.models import User
from app.schemas import CustomerCreate, CustomerResponse, CustomerUpdate
from app.services.customer_service import (
    add_customer,
    edit_customer,
    get_customer,
    get_customers,
    remove_customer,
)

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.post(
    "/",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db),
    officer: User = Depends(require_officer),
):
    """Only officers can create customer records."""
    return add_customer(db, customer)


@router.get("/", response_model=list[CustomerResponse])
def read_customers(
    db: Session = Depends(get_db),
    officer: User = Depends(require_officer),
):
    """Only officers can view the complete customer list."""
    return get_customers(db)


@router.get("/{customer_id}", response_model=CustomerResponse)
def read_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Officers can view any customer; customers can view only themselves."""
    if current_user.role == "CUSTOMER":
        if current_user.customer_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account is not linked to a customer record",
            )

        if current_user.customer_id != customer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can view only your own customer details",
            )

    elif current_user.role != "OFFICER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view customer details",
        )

    return get_customer(db, customer_id)


@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    customer: CustomerUpdate,
    db: Session = Depends(get_db),
    officer: User = Depends(require_officer),
):
    """Only officers can replace customer details."""
    return edit_customer(db, customer_id, customer)


@router.patch("/{customer_id}", response_model=CustomerResponse)
def partially_update_customer(
    customer_id: int,
    customer: CustomerUpdate,
    db: Session = Depends(get_db),
    officer: User = Depends(require_officer),
):
    """Only officers can update customer details."""
    return edit_customer(db, customer_id, customer)


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    officer: User = Depends(require_officer),
):
    """Only officers can delete customer records."""
    remove_customer(db, customer_id)
    return None
