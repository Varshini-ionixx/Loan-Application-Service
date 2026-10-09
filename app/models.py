from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base import Base


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    name: Mapped[str] = mapped_column(String(50), nullable=False)

    email: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )

    phone: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None)
    )

    loans: Mapped[list["Loan"]] = relationship(
        back_populates="customer", cascade="all, delete"
    )


class Loan(Base):
    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)

    amount: Mapped[float] = mapped_column(Float, nullable=False)

    tenure_months: Mapped[int] = mapped_column(nullable=False)

    interest_rate: Mapped[float] = mapped_column(Float, nullable=False)

    monthly_emi: Mapped[float] = mapped_column(Float, nullable=False)

    status: Mapped[str] = mapped_column(String(20), default="PENDING")

    rejection_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)

    applied_on: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None)
    )
    customer: Mapped["Customer"] = relationship(back_populates="loans")
