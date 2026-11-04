from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from day4_langgraph.prescreen_graph import CASES
from day5_capstone.approval_graph import SERDE, builder

graph = builder.compile(checkpointer=InMemorySaver(serde=SERDE))

customer_id, email, expected = CASES[3]
config = {
    "configurable": {"thread_id": "meera-1"},
    "run_name": "day5-lab2-meera",
    "tags": ["day5", "lab2"],
}

print("=== Run 1: start Meera's application ===")
result = graph.invoke({"customer_id": customer_id, "email": email, "log": []}, config=config)

for item in result["__interrupt__"]:
    print("PAUSED. Waiting for the officer:")
    for key, value in item.value.items():
        print(f"   {key:<14}: {value}")

snapshot = graph.get_state(config)
print("next     :", snapshot.next)
print("decision :", snapshot.values.get("decision", "(not decided yet)"))

print("\n=== Run 2: the officer answers ===")
officer_answer = {
    "decision": "approve",
    "officer": "Officer Rao",
    "note": "stable income, EMI well within limit",
}
result = graph.invoke(Command(resume=officer_answer), config=config)

print("decision :", result["decision"])
print("reason   :", result["reason"])
for line in result["log"]:
    print("   ", line)
print("next     :", graph.get_state(config).next)