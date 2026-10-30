import operator
from typing import Annotated, Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from day1_langchain.extractor import read_enquiry
from day1_langchain.schema import LoanEnquiry


class State(TypedDict):
    email: str
    enquiry: LoanEnquiry
    missing: list[str]
    decision: str
    log: Annotated[list[str], operator.add]


def intake(state: State) -> dict:
    enquiry = read_enquiry(state["email"])
    return {"enquiry": enquiry, "log": [f"intake: model read {enquiry.model_dump()}"]}


def validate(state: State) -> dict:
    enquiry = state["enquiry"]
    missing = []
    if enquiry.amount is None:
        missing.append("loan amount")
    if enquiry.tenure_months is None:
        missing.append("tenure")
    return {"missing": missing, "log": [f"validate: missing {missing or 'nothing'}"]}


def route(state: State) -> Literal["ready", "need_info"]:
    if state["missing"]:
        return "need_info"
    return "ready"


def ready(state: State) -> dict:
    enquiry = state["enquiry"]
    return {
        "decision": "ready",
        "log": [f"ready: {enquiry.amount:,.0f} for {enquiry.tenure_months} months can be scored"],
    }


def need_info(state: State) -> dict:
    return {
        "decision": "need_info",
        "log": [f"need_info: please tell us your {' and '.join(state['missing'])}"],
    }


builder = StateGraph(State)
builder.add_node("intake", intake)
builder.add_node("validate", validate)
builder.add_node("ready", ready)
builder.add_node("need_info", need_info)
builder.add_edge(START, "intake")
builder.add_edge("intake", "validate")
builder.add_conditional_edges("validate", route, ["ready", "need_info"])
builder.add_edge("ready", END)
builder.add_edge("need_info", END)
graph = builder.compile()

EMAILS = [
    "Hi, I'm Ramesh Kumar. I need a loan of 5 lakh rupees for 3 years to renovate my house.",
    "Hello, I am Priya. I would like a loan for a two-wheeler.",
    "Kavya here. I need 3 lakhs for my daughter's college fees.",
]

for number, email in enumerate(EMAILS, start=1):
    result = graph.invoke(
        {"email": email, "log": []},
        config={"run_name": f"day4-lab5-email{number}", "tags": ["day4", "lab5"]},
    )
    print(f"\n=== EMAIL {number}: {email}")
    print("Decision:", result["decision"])
    for line in result["log"]:
        print("  ", line)