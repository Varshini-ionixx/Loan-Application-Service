from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Customer
from app.repositories.customer_repository import (
    create_customer,
    delete_customer,
    get_all_customers,
    get_customer_by_email,
    get_customer_by_id,
    update_customer,
)
from app.schemas import CustomerCreate, CustomerUpdate


def add_customer(db: Session, customer_data: CustomerCreate):

    existing_customer = get_customer_by_email(db, customer_data.email)

    if existing_customer:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already exists"
        )

    customer = Customer(
        name=customer_data.name, email=customer_data.email, phone=customer_data.phone
    )

    return create_customer(db, customer)


def get_customer(db: Session, customer_id: int):

    customer = get_customer_by_id(db, customer_id)

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return customer


def get_customers(db: Session):

    return get_all_customers(db)


def edit_customer(db: Session, customer_id: int, customer_data: CustomerUpdate):

    customer = get_customer_by_id(db, customer_id)

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    data = customer_data.model_dump(exclude_unset=True)

    return update_customer(db, customer, data)


def remove_customer(db: Session, customer_id: int):

    customer = get_customer_by_id(db, customer_id)

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    delete_customer(db, customer)

    return {"message": "Customer deleted successfully"}
