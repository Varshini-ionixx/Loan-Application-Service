import operator
import sys
from typing import Annotated, Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from day1_langchain.extractor import read_enquiry
from day1_langchain.schema import LoanEnquiry
from day2_agents.tools import emi_calculator, get_customer

ANNUAL_RATE_PERCENT = 11
MIN_AGE = 21
MAX_AGE = 60
MIN_MONTHLY_INCOME = 25000
MIN_CREDIT_SCORE = 650
REFER_BELOW_CREDIT_SCORE = 700
MAX_EMI_TO_INCOME_RATIO = 0.5
REFER_ABOVE_AMOUNT = 1000000


class State(TypedDict):
    customer_id: int
    email: str
    enquiry: LoanEnquiry
    customer: dict
    missing: list[str]
    emi: float
    failed_rules: list[str]
    refer_reasons: list[str]
    decision: str
    reason: str
    log: Annotated[list[str], operator.add]


def intake(state: State) -> dict:
    enquiry = read_enquiry(state["email"])
    return {"enquiry": enquiry, "log": [f"intake: model read {enquiry.model_dump()}"]}


def validate(state: State) -> dict:
    enquiry = state["enquiry"]
    missing = []
    if enquiry.amount is None or enquiry.amount <= 0:
        missing.append("loan amount is missing")
    if enquiry.tenure_months is None or enquiry.tenure_months <= 0:
        missing.append("tenure is missing")

    customer = get_customer.invoke({"customer_id": state["customer_id"]})
    if isinstance(customer, str):
        missing.append(customer)
        customer = {}

    found = customer.get("name", "no customer")
    return {
        "customer": customer,
        "missing": missing,
        "log": [f"validate: customer {state['customer_id']} -> {found}; missing {missing or 'nothing'}"],
    }


def after_validate(state: State) -> Literal["need_info", "score"]:
    if state["missing"]:
        return "need_info"
    return "score"


def score(state: State) -> dict:
    enquiry = state["enquiry"]
    customer = state["customer"]

    emi = emi_calculator.invoke(
        {
            "principal": enquiry.amount,
            "annual_rate_percent": ANNUAL_RATE_PERCENT,
            "tenure_months": enquiry.tenure_months,
        }
    )

    age = customer["age"]
    income = customer["monthly_income"]
    credit = customer["credit_score"]
    total_emi = customer["existing_emi"] + emi
    limit = MAX_EMI_TO_INCOME_RATIO * income

    failed_rules = []
    if not MIN_AGE <= age <= MAX_AGE:
        failed_rules.append(f"age must be {MIN_AGE}-{MAX_AGE} (customer is {age})")
    if income < MIN_MONTHLY_INCOME:
        failed_rules.append(f"monthly income must be at least {MIN_MONTHLY_INCOME:,} (customer has {income:,.0f})")
    if credit < MIN_CREDIT_SCORE:
        failed_rules.append(f"credit score must be at least {MIN_CREDIT_SCORE} (customer has {credit})")
    if total_emi > limit:
        failed_rules.append(f"total EMI {total_emi:,.0f} is above 50% of income ({limit:,.0f})")

    refer_reasons = []
    if MIN_CREDIT_SCORE <= credit < REFER_BELOW_CREDIT_SCORE:
        refer_reasons.append(f"credit score {credit} is between {MIN_CREDIT_SCORE} and {REFER_BELOW_CREDIT_SCORE - 1}")
    if enquiry.amount > REFER_ABOVE_AMOUNT:
        refer_reasons.append(f"amount {enquiry.amount:,.0f} is above {REFER_ABOVE_AMOUNT:,}")

    return {
        "emi": emi,
        "failed_rules": failed_rules,
        "refer_reasons": refer_reasons,
        "log": [f"score: EMI {emi:,.2f}, total EMI {total_emi:,.0f} of {limit:,.0f} allowed, credit {credit}"],
    }


def decide(state: State) -> Literal["reject", "refer", "approve"]:
    if state["failed_rules"]:
        return "reject"
    if state["refer_reasons"]:
        return "refer"
    return "approve"


def need_info(state: State) -> dict:
    reason = "Cannot pre-screen yet: " + "; ".join(state["missing"])
    return {"decision": "need_info", "reason": reason, "log": [f"need_info: {reason}"]}


def reject(state: State) -> dict:
    reason = "Does not meet: " + "; ".join(state["failed_rules"])
    return {"decision": "reject", "reason": reason, "log": [f"reject: {reason}"]}


def refer(state: State) -> dict:
    reason = "Needs a senior officer: " + "; ".join(state["refer_reasons"])
    return {"decision": "refer", "reason": reason, "log": [f"refer: {reason}"]}


def approve(state: State) -> dict:
    enquiry = state["enquiry"]
    reason = (
        f"Meets all rules. EMI {state['emi']:,.2f} at {ANNUAL_RATE_PERCENT}% "
        f"for {enquiry.tenure_months} months."
    )
    return {"decision": "approve", "reason": reason, "log": [f"approve: {reason}"]}


builder = StateGraph(State)
builder.add_node("intake", intake)
builder.add_node("validate", validate)
builder.add_node("score", score)
builder.add_node("need_info", need_info)
builder.add_node("reject", reject)
builder.add_node("refer", refer)
builder.add_node("approve", approve)

builder.add_edge(START, "intake")
builder.add_edge("intake", "validate")
builder.add_conditional_edges("validate", after_validate, ["need_info", "score"])
builder.add_conditional_edges("score", decide, ["reject", "refer", "approve"])
for outcome in ["need_info", "reject", "refer", "approve"]:
    builder.add_edge(outcome, END)

graph = builder.compile()

MEERA_ID = 12  # replace with Meera Iyer's real customer ID from Step 0.2

CASES = {
    1: (4, "Hi, this is customer 4. I need 5 lakh for 3 years to renovate my house.", "approve"),
    2: (5, "Hello, I want a loan of 4 lakh for 2 years for my shop.", "reject"),
    3: (MEERA_ID, "I'm Meera Iyer. I need 5 lakh for 3 years for my wedding.", "refer"),
    4: (4, "I would like 12 lakh over 5 years to buy a car.", "refer"),
    5: (9999, "Please give me 2 lakh for 1 year.", "need_info"),
    6: (4, "I want a loan for my child's education. Please call me.", "need_info"),
}


def run(number: int) -> bool:
    customer_id, email, expected = CASES[number]
    result = graph.invoke(
        {"customer_id": customer_id, "email": email, "log": []},
        config={"run_name": f"day4-prescreen-case{number}", "tags": ["day4", "prescreen"]},
    )
    passed = result["decision"] == expected

    print(f"\n=== CASE {number}: customer {customer_id} | {email}")
    print(f"Decision: {result['decision']}  (expected {expected})  {'PASS' if passed else 'FAIL'}")
    print("Reason  :", result["reason"])
    for line in result["log"]:
        print("   ", line)
    return passed


if __name__ == "__main__":
    chosen = [int(arg) for arg in sys.argv[1:]] or list(CASES)
    results = [run(number) for number in chosen]
    print(f"\n{sum(results)}/{len(results)} cases passed")