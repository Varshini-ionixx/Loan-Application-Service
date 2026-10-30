import operator
from typing import Annotated, Literal, TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    amount: float
    decision: str
    log: Annotated[list[str], operator.add]


def check(state: State) -> dict:
    return {"log": [f"check: amount {state['amount']:,.0f}"]}


def route(state: State) -> Literal["auto_approve", "senior_review"]:
    if state["amount"] > 1000000:
        return "senior_review"
    return "auto_approve"


def auto_approve(state: State) -> dict:
    return {"decision": "approve", "log": ["auto_approve: within the auto-approval limit"]}


def senior_review(state: State) -> dict:
    return {"decision": "refer", "log": ["senior_review: above 10,00,000, needs a senior officer"]}


builder = StateGraph(State)
builder.add_node("check", check)
builder.add_node("auto_approve", auto_approve)
builder.add_node("senior_review", senior_review)
builder.add_edge(START, "check")
builder.add_conditional_edges("check", route, ["auto_approve", "senior_review"])
builder.add_edge("auto_approve", END)
builder.add_edge("senior_review", END)
graph = builder.compile()

print(graph.get_graph().draw_mermaid())

for amount in [500000, 1500000]:
    print(f"\n=== amount {amount:,} ===")
    for update in graph.stream({"amount": amount, "log": []}, stream_mode="updates"):
        print(update)