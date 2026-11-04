from langchain_core.tracers.langchain import wait_for_all_tracers
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from day4_langgraph.prescreen_graph import CASES
from day5_capstone.approval_graph import SERDE, builder

graph = builder.compile(checkpointer=InMemorySaver(serde=SERDE))


def show(updates) -> None:
    for update in updates:
        for node, change in update.items():
            if node == "__interrupt__":
                print(f"  [PAUSE] waiting for the officer: {change[0].value['reason']}")
            else:
                print(f"  [{node}] changed {list(change)}")
                for line in change.get("log", []):
                    print(f"      log: {line}")


customer_id, email, expected = CASES[3]
config = {
    "configurable": {"thread_id": "meera-stream-1"},
    "run_name": "day5-lab4-meera",
    "tags": ["day5", "lab4"],
}

print("=== Part 1: stream until the pause ===")
show(graph.stream({"customer_id": customer_id, "email": email, "log": []}, config=config, stream_mode="updates"))

print("\n=== Part 2: the officer rejects, stream the rest ===")
officer_answer = {
    "decision": "reject",
    "officer": "Officer Rao",
    "note": "recent missed payments on another loan",
}
show(graph.stream(Command(resume=officer_answer), config=config, stream_mode="updates"))

print("\nFinal decision:", graph.get_state(config).values["decision"])
wait_for_all_tracers()