import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph


class PlainState(TypedDict):
    amount: float
    log: list[str]


class LogState(TypedDict):
    amount: float
    log: Annotated[list[str], operator.add]


def validate(state) -> dict:
    return {"log": [f"validate: amount {state['amount']:,.0f} is present"]}


def score(state) -> dict:
    return {"log": ["score: EMI calculated"]}


def decide(state) -> dict:
    return {"log": ["decide: approved"]}


def build(state_type):
    builder = StateGraph(state_type)
    builder.add_node("validate", validate)
    builder.add_node("score", score)
    builder.add_node("decide", decide)
    builder.add_edge(START, "validate")
    builder.add_edge("validate", "score")
    builder.add_edge("score", "decide")
    builder.add_edge("decide", END)
    return builder.compile()


print("operator.add on two lists:", operator.add(["a"], ["b"]))

START_STATE = {"amount": 500000, "log": ["start: application received"]}

print("\n=== Without a reducer (replace) ===")
result = build(PlainState).invoke(START_STATE)
for line in result["log"]:
    print(" ", line)

print("\n=== With operator.add (append) ===")
result = build(LogState).invoke(START_STATE)
for line in result["log"]:
    print(" ", line)