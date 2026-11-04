from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

from day4_langgraph.prescreen_graph import CASES, builder

serde = JsonPlusSerializer(allowed_msgpack_modules=[("day1_langchain.schema", "LoanEnquiry")])
graph = builder.compile(checkpointer=InMemorySaver(serde=serde))

for number in [1, 5]:
    customer_id, email, expected = CASES[number]
    config = {
        "configurable": {"thread_id": f"case-{number}"},
        "run_name": f"day5-lab1-case{number}",
        "tags": ["day5", "lab1"],
    }
    result = graph.invoke({"customer_id": customer_id, "email": email, "log": []}, config=config)
    print(f"\n=== thread case-{number}: decision {result['decision']}")

print("\n--- Reading saved state back with get_state ---")
for number in [1, 5]:
    snapshot = graph.get_state({"configurable": {"thread_id": f"case-{number}"}})
    print(f"\nthread case-{number}")
    print("  decision :", snapshot.values["decision"])
    print("  reason   :", snapshot.values["reason"])
    print("  next     :", snapshot.next)
    print("  log lines:", len(snapshot.values["log"]))

print("\n--- History of thread case-1 (newest first) ---")
for snapshot in graph.get_state_history({"configurable": {"thread_id": "case-1"}}):
    print(f"  step {snapshot.metadata['step']:>2}  next={snapshot.next}")

unknown = graph.get_state({"configurable": {"thread_id": "case-99"}})
print("\nUnknown thread values:", unknown.values)