from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import CustomerCreate, CustomerResponse, CustomerUpdate
from app.services.customer_service import (
    add_customer,
    edit_customer,
    get_customer,
    get_customers,
    remove_customer,
)

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):

    return add_customer(db, customer)


@router.get("/", response_model=list[CustomerResponse])
def read_customers(db: Session = Depends(get_db)):

    return get_customers(db)


@router.get("/{customer_id}", response_model=CustomerResponse)
def read_customer(customer_id: int, db: Session = Depends(get_db)):

    return get_customer(db, customer_id)


@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int, customer: CustomerUpdate, db: Session = Depends(get_db)
):

    return edit_customer(db, customer_id, customer)


@router.patch("/{customer_id}", response_model=CustomerResponse)
def partial_update_customer(
    customer_id: int, customer: CustomerUpdate, db: Session = Depends(get_db)
):

    return edit_customer(db, customer_id, customer)


@router.delete("/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(get_db)):

    return remove_customer(db, customer_id)
