import sqlite3
import sys

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command
from langchain_core.tracers.langchain import wait_for_all_tracers


from day4_langgraph.prescreen_graph import CASES
from day5_capstone.approval_graph import SERDE, builder

DB_PATH = "checkpoints.db"
THREAD_ID = "meera-sqlite-1"

step = sys.argv[1] if len(sys.argv) > 1 else "status"

connection = sqlite3.connect(DB_PATH, check_same_thread=False)
graph = builder.compile(checkpointer=SqliteSaver(connection, serde=SERDE))
config = {
    "configurable": {"thread_id": THREAD_ID},
    "run_name": f"day5-lab3-{step}",
    "tags": ["day5", "lab3"],
}
snapshot = graph.get_state(config)

if step == "start":
    if snapshot.values:
        print(f"{THREAD_ID} was already started. Use 'status' or 'resume'.")
    else:
        customer_id, email, expected = CASES[3]
        result = graph.invoke({"customer_id": customer_id, "email": email, "log": []}, config=config)
        if "__interrupt__" in result:
            print(f"Started {THREAD_ID}. Paused for the officer:")
            print("  ", result["__interrupt__"][0].value["reason"])
            print(f"You can close this program now. The case is saved in {DB_PATH}.")
        else:
            print(f"{THREAD_ID} finished without needing an officer:")
            print("  ", result["decision"], "-", result["reason"])


elif step == "status":
    if not snapshot.values:
        print(f"No saved case for {THREAD_ID}. Run 'start' first.")
    else:
        print("thread   :", THREAD_ID)
        print("next     :", snapshot.next)
        print("decision :", snapshot.values.get("decision", "(waiting for the officer)"))
        for line in snapshot.values["log"]:
            print("   ", line)

elif step == "resume":
    if snapshot.next != ("refer",):
        print(f"{THREAD_ID} is not waiting for an officer.")
    else:
        officer_answer = {
            "decision": "approve",
            "officer": "Officer Rao",
            "note": "stable income, EMI well within limit",
        }
        result = graph.invoke(Command(resume=officer_answer), config=config)
        print("decision :", result["decision"])
        print("reason   :", result["reason"])

wait_for_all_tracers()
connection.close()