import httpx
from dotenv import load_dotenv
from langchain.tools import tool

from loan_api_client.client import LoanApiClient

load_dotenv()

api = LoanApiClient()

@tool
def emi_calculator(principal: float, annual_rate_percent: float, tenure_months: int) -> float | str:
    """Calculate the monthly EMI of a loan.
    principal is in rupees, annual_rate_percent is like 11 for 11 percent,
    tenure_months is the loan length in months.
    Returns the EMI, or a message explaining which input is invalid."""
    if principal <= 0:
        return "Principal must be a positive amount in rupees."
    if annual_rate_percent <= 0:
        return "Annual interest rate must be positive, for example 11 for 11 percent."
    if tenure_months <= 0:
        return "Tenure must be a positive number of months."
    monthly_rate = annual_rate_percent / (12 * 100)
    growth = (1 + monthly_rate) ** tenure_months
    emi = principal * monthly_rate * growth / (growth - 1)
    return round(emi, 2)

PROFILE_FIELDS = ("age", "monthly_income", "existing_emi", "credit_score")

@tool
def get_customer(customer_id: int) -> dict | str:
    """Look up a customer in the loan system by their numeric customer ID.
    Returns the customer's name, age, monthly_income (rupees per month),
    existing_emi (rupees per month already being paid) and credit_score,
    or a message if the customer cannot be found."""
    try:
        customer = api.get_customer(customer_id)
    except httpx.HTTPError:
        return "The loan system is not reachable right now. Please try again later."

    if customer is None:
        return f"Customer {customer_id} not found."

    missing = [field for field in PROFILE_FIELDS if customer.get(field) is None]
    if missing:
        return f"Customer {customer_id} has an incomplete profile. Missing: {', '.join(missing)}."

    return {"name": customer["name"], **{field: customer[field] for field in PROFILE_FIELDS}}

@tool
def check_eligibility(
    age: int, monthly_income: float, existing_emi: float, credit_score: int, new_emi: float
) -> dict:
    """Check a customer against the loan eligibility rules.
    monthly_income, existing_emi and new_emi are rupees per month;
    new_emi is the EMI of the requested loan, from emi_calculator.
    Returns whether the customer is eligible and every rule they fail."""
    failed_rules = []

    if not 21 <= age <= 60:
        failed_rules.append(f"Age must be between 21 and 60 (customer is {age})")
    if monthly_income < 25000:
        failed_rules.append(f"Monthly income must be at least 25,000 (customer has {monthly_income:,.0f})")
    if credit_score < 700:
        failed_rules.append(f"Credit score must be at least 700 (customer has {credit_score})")

    total_emi = existing_emi + new_emi
    limit = 0.5 * monthly_income
    if total_emi > limit:
        failed_rules.append(
            f"Existing EMI plus new EMI ({total_emi:,.0f}) must be at most 50% of monthly income ({limit:,.0f})"
        )

    return {"eligible": not failed_rules, "failed_rules": failed_rules}