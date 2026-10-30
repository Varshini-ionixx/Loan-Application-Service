from typing import Optional

from pydantic import BaseModel, Field


class LoanEnquiry(BaseModel):
    customer_name: Optional[str] = Field(None, description="Full name if stated, otherwise null")
    amount: Optional[float] = Field(None, description="Loan amount in rupees")
    tenure_months: Optional[int] = Field(None, description="Tenure converted to months")
    purpose: Optional[str] = Field(None, description="Why the loan is needed")