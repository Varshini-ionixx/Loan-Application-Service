from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from day4_langgraph.prescreen_graph import (
    State,
    after_validate,
    approve,
    decide,
    intake,
    need_info,
    reject,
    score,
    validate,
)

SERDE = JsonPlusSerializer(allowed_msgpack_modules=[("day1_langchain.schema", "LoanEnquiry")])


def refer_to_officer(state: State) -> dict:
    reason = "Needs a senior officer: " + "; ".join(state["refer_reasons"])
    enquiry = state["enquiry"]

    answer = interrupt(
        {
            "customer_id": state["customer_id"],
            "amount": enquiry.amount,
            "tenure_months": enquiry.tenure_months,
            "emi": state["emi"],
            "reason": reason,
            "question": "Approve or reject this loan?",
        }
    )

    decision = answer["decision"]
    officer = answer["officer"]
    note = answer["note"]
    return {
        "decision": decision,
        "reason": f"{reason}. {officer} chose {decision}: {note}",
        "log": [f"refer: {reason}", f"officer: {officer} chose {decision} - {note}"],
    }


builder = StateGraph(State)
builder.add_node("intake", intake)
builder.add_node("validate", validate)
builder.add_node("score", score)
builder.add_node("need_info", need_info)
builder.add_node("reject", reject)
builder.add_node("refer", refer_to_officer)
builder.add_node("approve", approve)

builder.add_edge(START, "intake")
builder.add_edge("intake", "validate")
builder.add_conditional_edges("validate", after_validate, ["need_info", "score"])
builder.add_conditional_edges("score", decide, ["reject", "refer", "approve"])
for outcome in ["need_info", "reject", "refer", "approve"]:
    builder.add_edge(outcome, END)