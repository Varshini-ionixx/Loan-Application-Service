from sqlalchemy.orm import Session
 
from app.models import Customer
 
 
def create_customer(
    db: Session,
    customer: Customer
):
 
    db.add(customer)
    db.commit()
    db.refresh(customer)
 
    return customer
 
 
 
def get_customer_by_id(
    db: Session,
    customer_id: int
):
 
    return db.query(Customer).filter(
        Customer.id == customer_id
    ).first()
 
 
 
def get_customer_by_email(
    db: Session,
    email: str
):
 
    return db.query(Customer).filter(
        Customer.email == email
    ).first()
 
 
 
def get_all_customers(
    db: Session
):
 
    return db.query(Customer).all()
 
 
 
def update_customer(
    db: Session,
    customer: Customer,
    update_data: dict
):
 
    for key, value in update_data.items():
        setattr(customer, key, value)
 
    db.commit()
    db.refresh(customer)
 
    return customer
 
 
 
def delete_customer(
    db: Session,
    customer: Customer
):
 
    db.delete(customer)
    db.commit()
 