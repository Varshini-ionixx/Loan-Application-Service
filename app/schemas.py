from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

# ==========================
# Customer Schemas
# ==========================


class CustomerCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    age: int = Field(ge=18, le=100)
    monthly_income: float = Field(ge=0)
    existing_emi: float = Field(default=0, ge=0)
    credit_score: int = Field(ge=300, le=900)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        if len(value.strip()) < 3:
            raise ValueError("Name must contain at least 3 characters")

        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value):
        if len(value) != 10:
            raise ValueError("Phone number must contain exactly 10 digits")

        if not value.isdigit():
            raise ValueError("Phone number must contain only digits")

        return value


class CustomerUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    age: int | None = Field(default=None, ge=18, le=100)
    monthly_income: float | None = Field(default=None, ge=0)
    existing_emi: float | None = Field(default=None, ge=0)
    credit_score: int | None = Field(default=None, ge=300, le=900)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value):
        if value is not None:
            if len(value) != 10:
                raise ValueError("Phone number must contain exactly 10 digits")

            if not value.isdigit():
                raise ValueError("Phone number must contain only digits")

        return value


class CustomerResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str
    age: int | None
    monthly_income: float | None
    existing_emi: float | None
    credit_score: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================
# Loan Schemas
# ==========================


class LoanCreate(BaseModel):
    customer_id: int
    amount: float
    tenure_months: int


class LoanUpdate(BaseModel):
    amount: float | None = None
    tenure_months: int | None = None
    status: str | None = None
    rejection_reason: str | None = None


class LoanResponse(BaseModel):
    id: int
    customer_id: int
    amount: float
    tenure_months: int
    interest_rate: float
    monthly_emi: float
    status: str
    rejection_reason: str | None
    applied_on: datetime

    model_config = ConfigDict(from_attributes=True)


class LoanPageResponse(BaseModel):
    items: list[LoanResponse]
    page: int
    size: int
    total: int
    pages: int


class Token(BaseModel):
    access_token: str
    token_type: str
