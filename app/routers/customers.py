from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/customers", tags=["customers"])


# CREATE CUSTOMER
@router.post("/", response_model=schemas.CustomerResponse)
def create_customer(
    customer: schemas.CustomerCreate,
    db: Session = Depends(get_db)
):
    existing_customer = db.query(models.Customer).filter(
        models.Customer.email == customer.email
    ).first()

    if existing_customer:
        raise HTTPException(
            status_code=400,
            detail="Customer with this email already exists"
        )

    db_customer = models.Customer(
        name=customer.name,
        email=customer.email,
        phone_number=customer.phone_number
    )

    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)

    return db_customer


# GET CUSTOMER
@router.get("/{customer_id}", response_model=schemas.CustomerResponse)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    customer = db.get(models.Customer, customer_id)

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    return customer


# UPDATE CUSTOMER
@router.put("/{customer_id}", response_model=schemas.CustomerResponse)
def update_customer(
    customer_id: int,
    customer: schemas.CustomerCreate,
    db: Session = Depends(get_db)
):
    existing_customer = db.get(models.Customer, customer_id)

    if existing_customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    # Check whether the new email belongs to another customer
    email_customer = db.query(models.Customer).filter(
        models.Customer.email == customer.email,
        models.Customer.id != customer_id
    ).first()

    if email_customer:
        raise HTTPException(
            status_code=400,
            detail="Another customer with this email already exists"
        )

    # Check whether the new phone number belongs to another customer
    phone_customer = db.query(models.Customer).filter(
        models.Customer.phone_number == customer.phone_number,
        models.Customer.id != customer_id
    ).first()

    if phone_customer:
        raise HTTPException(
            status_code=400,
            detail="Another customer with this phone number already exists"
        )

    existing_customer.name = customer.name
    existing_customer.email = customer.email
    existing_customer.phone_number = customer.phone_number

    db.commit()
    db.refresh(existing_customer)

    return existing_customer


# DELETE CUSTOMER
@router.delete("/{customer_id}")
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    customer = db.get(models.Customer, customer_id)

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    db.delete(customer)
    db.commit()

    return {
        "message": "Customer deleted successfully",
        "customer_id": customer_id
    }


@router.patch("/{customer_id}", response_model=schemas.CustomerResponse)
def patch_customer(
    customer_id: int,
    customer: schemas.CustomerUpdate,
    db: Session = Depends(get_db)
):
    existing_customer = db.get(models.Customer, customer_id)

    if existing_customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    # Get only the fields that were actually provided
    update_data = customer.model_dump(exclude_unset=True)

    # Check email uniqueness only if email is being updated
    if "email" in update_data:
        email_customer = db.query(models.Customer).filter(
            models.Customer.email == update_data["email"],
            models.Customer.id != customer_id
        ).first()

        if email_customer:
            raise HTTPException(
                status_code=400,
                detail="Another customer with this email already exists"
            )

    # Check phone uniqueness only if phone_number is being updated
    if "phone_number" in update_data:
        phone_customer = db.query(models.Customer).filter(
            models.Customer.phone_number == update_data["phone_number"],
            models.Customer.id != customer_id
        ).first()

        if phone_customer:
            raise HTTPException(
                status_code=400,
                detail="Another customer with this phone number already exists"
            )

    # Update only the fields provided in the request
    for field, value in update_data.items():
        setattr(existing_customer, field, value)

    db.commit()
    db.refresh(existing_customer)

    return existing_customer
