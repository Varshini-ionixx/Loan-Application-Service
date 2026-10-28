from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Customer, Loan
from app.repositories.customer_repository import get_customer_by_id
from app.repositories.loan_repository import (
    create_loan,
    delete_loan,
    get_all_loans,
    get_loan_by_id,
    update_loan,
)
from app.schemas import LoanCreate, LoanUpdate

# Eligibility rules from the loan policy (sections 1.1 to 1.4 and 2.3).
MIN_AGE = 21
MAX_AGE = 60
MIN_MONTHLY_INCOME = 25000
MIN_CREDIT_SCORE = 650
REFER_BELOW_CREDIT_SCORE = 700
MAX_EMI_TO_INCOME_RATIO = 0.5
REFER_ABOVE_AMOUNT = 1000000

PROFILE_FIELDS = ("age", "monthly_income", "existing_emi", "credit_score")


def calculate_emi(amount: float, rate: float, tenure: int):
    monthly_rate = rate / (12 * 100)

    emi = (amount * monthly_rate * (1 + monthly_rate) ** tenure) / (
        ((1 + monthly_rate) ** tenure) - 1
    )

    return round(emi, 2)


def failed_eligibility_rules(customer: Customer, new_emi: float) -> list[str]:
    """Return every rule the customer fails; an empty list means none."""
    failed = []

    if not MIN_AGE <= customer.age <= MAX_AGE:
        failed.append(f"Age must be between {MIN_AGE} and {MAX_AGE}")

    if customer.monthly_income < MIN_MONTHLY_INCOME:
        failed.append(f"Monthly income must be at least {MIN_MONTHLY_INCOME}")

    if customer.credit_score < MIN_CREDIT_SCORE:
        failed.append(f"Credit score must be at least {MIN_CREDIT_SCORE}")

    total_emi = customer.existing_emi + new_emi
    if total_emi > MAX_EMI_TO_INCOME_RATIO * customer.monthly_income:
        failed.append("Existing EMI plus new EMI exceeds 50% of monthly income")

    return failed


def referral_reasons(customer: Customer, amount: float) -> list[str]:
    """Return why the loan needs an officer's review; empty if it does not."""
    reasons = []

    if customer.credit_score < REFER_BELOW_CREDIT_SCORE:
        reasons.append(
            f"Credit score between {MIN_CREDIT_SCORE} and "
            f"{REFER_BELOW_CREDIT_SCORE - 1} is referred to a credit officer"
        )

    if amount > REFER_ABOVE_AMOUNT:
        reasons.append(
            f"Loans above {REFER_ABOVE_AMOUNT} require senior manager approval"
        )

    return reasons


def apply_loan(db: Session, loan_data: LoanCreate):
    try:
        customer = get_customer_by_id(db, loan_data.customer_id)

        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")

        rate_map = {12: 10, 24: 11, 36: 12, 48: 13, 60: 13}
        rate = rate_map.get(loan_data.tenure_months)

        if rate is None:
            raise HTTPException(status_code=400, detail="Invalid tenure")

        missing = [
            field for field in PROFILE_FIELDS if getattr(customer, field) is None
        ]
        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"Customer profile is missing: {', '.join(missing)}",
            )

        emi = calculate_emi(loan_data.amount, rate, loan_data.tenure_months)

        # Priority order: any failed rule rejects, then referral, then approval.
        failed = failed_eligibility_rules(customer, emi)
        referrals = referral_reasons(customer, loan_data.amount)

        if failed:
            status, reason = "REJECTED", "; ".join(failed)
        elif referrals:
            status, reason = "REFERRED", "; ".join(referrals)
        else:
            status, reason = "APPROVED", None

        loan = Loan(
            customer_id=loan_data.customer_id,
            amount=loan_data.amount,
            tenure_months=loan_data.tenure_months,
            interest_rate=rate,
            monthly_emi=emi,
            status=status,
            rejection_reason=reason,
        )

        created_loan = create_loan(db, loan)
        db.commit()
        db.refresh(created_loan)

        return created_loan

    except Exception:
        db.rollback()
        raise


def get_loan(db: Session, loan_id: int):
    loan = get_loan_by_id(db, loan_id)

    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")

    return loan


def get_loans(
    db: Session,
    status_filter: str | None = None,
    customer_id: int | None = None,
    page: int = 1,
    size: int = 10,
):
    loans, total = get_all_loans(
        db,
        status_filter=status_filter,
        customer_id=customer_id,
        page=page,
        size=size,
    )

    pages = (total + size - 1) // size

    return {
        "items": loans,
        "page": page,
        "size": size,
        "total": total,
        "pages": pages,
    }


def edit_loan(db: Session, loan_id: int, loan_data: LoanUpdate):
    try:
        loan = get_loan_by_id(db, loan_id)

        if not loan:
            raise HTTPException(status_code=404, detail="Loan not found")

        data = loan_data.model_dump(exclude_unset=True)
        updated_loan = update_loan(db, loan, data)

        db.commit()
        db.refresh(updated_loan)

        return updated_loan

    except Exception:
        db.rollback()
        raise


def remove_loan(db: Session, loan_id: int):
    try:
        loan = get_loan_by_id(db, loan_id)

        if not loan:
            raise HTTPException(status_code=404, detail="Loan not found")

        delete_loan(db, loan)
        db.commit()

        return {"message": "Loan deleted successfully"}

    except Exception:
        db.rollback()
        raise
