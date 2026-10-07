from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import get_db, engine
from app.routers import customers
from app import models
from app.base import Base
app = FastAPI()
Base.metadata.create_all(bind=engine)
app.include_router(customers.router)
@app.get("")
def root():
    return {"message": "Loan application service is running"}