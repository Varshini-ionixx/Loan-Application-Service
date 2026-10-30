from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    amount: float
    decision: str


def check(state: State) -> dict:
    print(f"\ncheck received amount: {state['amount']:,.0f}")
    return {}


def route(state: State) -> Literal["auto_approve", "senior_review"]:
    if state["amount"] > 1000000:
        return "senior_review"
    return "auto_approve"


def auto_approve(state: State) -> dict:
    print("auto_approve ran")
    return {"decision": "Approved automatically"}


def senior_review(state: State) -> dict:
    print("senior_review ran")
    return {"decision": "Sent to a senior officer (amount above 10,00,000)"}


builder = StateGraph(State)

builder.add_node("check", check)
builder.add_node("auto_approve", auto_approve)
builder.add_node("senior_review", senior_review)

builder.add_edge(START, "check")
builder.add_conditional_edges("check", route, ["auto_approve", "senior_review"])
builder.add_edge("auto_approve", END)
builder.add_edge("senior_review", END)

graph = builder.compile()

for amount in [500000, 1500000]:
    result = graph.invoke({"amount": amount})
    print("Final state:", result)