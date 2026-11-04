import sqlite3
import sys

from langchain_core.tracers.langchain import wait_for_all_tracers
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command

from day4_langgraph.prescreen_graph import CASES
from day5_capstone.approval_graph import SERDE, builder

DB_PATH = "checkpoints.db"
OFFICER_NAME = "Officer Rao"
USAGE = """Usage:
  start <case number>                          run a test case (1-6)
  pending                                      list cases waiting for an officer
  show <thread id>                             show a case's status and log
  decide <thread id> <approve|reject> <note>   the officer decides a waiting case"""

connection = sqlite3.connect(DB_PATH, check_same_thread=False)
checkpointer = SqliteSaver(connection, serde=SERDE)
graph = builder.compile(checkpointer=checkpointer)


def config_for(thread_id: str, action: str) -> dict:
    return {
        "configurable": {"thread_id": thread_id},
        "run_name": f"day5-officer-{action}-{thread_id}",
        "tags": ["day5", "officer-app"],
    }


def start(number: int) -> None:
    if number not in CASES:
        print(f"There is no case {number}. Choose 1-{len(CASES)}.")
        return
    thread_id = f"case-{number}"
    config = config_for(thread_id, "start")
    if graph.get_state(config).values:
        print(f"{thread_id} already exists. Use 'show {thread_id}'.")
        return

    customer_id, email, expected = CASES[number]
    result = graph.invoke({"customer_id": customer_id, "email": email, "log": []}, config=config)
    if "__interrupt__" in result:
        print(f"{thread_id}: waiting for an officer - {result['__interrupt__'][0].value['reason']}")
    else:
        print(f"{thread_id}: {result['decision']} - {result['reason']}")


def pending() -> None:
    thread_ids = sorted({saved.config["configurable"]["thread_id"] for saved in checkpointer.list(None)})
    waiting = 0
    for thread_id in thread_ids:
        snapshot = graph.get_state(config_for(thread_id, "pending"))
        if snapshot.next != ("refer",):
            continue
        waiting += 1
        case = snapshot.interrupts[0].value
        print(
            f"{thread_id}: customer {case['customer_id']}, {case['amount']:,.0f} for "
            f"{case['tenure_months']} months, EMI {case['emi']:,.2f}"
        )
        print(f"    {case['reason']}")
    if not waiting:
        print("No cases are waiting for an officer.")


def show(thread_id: str) -> None:
    snapshot = graph.get_state(config_for(thread_id, "show"))
    if not snapshot.values:
        print(f"No case called {thread_id}.")
        return
    status = "waiting for an officer" if snapshot.next else snapshot.values["decision"]
    print(f"{thread_id}: {status}")
    for line in snapshot.values["log"]:
        print("   ", line)


def decide(thread_id: str, decision: str, note: str) -> None:
    if decision not in ("approve", "reject"):
        print("The decision must be 'approve' or 'reject'.")
        return
    config = config_for(thread_id, "decide")
    if graph.get_state(config).next != ("refer",):
        print(f"{thread_id} is not waiting for an officer.")
        return

    answer = {"decision": decision, "officer": OFFICER_NAME, "note": note}
    result = graph.invoke(Command(resume=answer), config=config)
    print(f"{thread_id}: {result['decision']} - {result['reason']}")


def main(args: list[str]) -> None:
    command = args[0] if args else ""
    if command == "start" and len(args) == 2:
        start(int(args[1]))
    elif command == "pending" and len(args) == 1:
        pending()
    elif command == "show" and len(args) == 2:
        show(args[1])
    elif command == "decide" and len(args) >= 4:
        decide(args[1], args[2], " ".join(args[3:]))
    else:
        print(USAGE)


if __name__ == "__main__":
    main(sys.argv[1:])
    wait_for_all_tracers()
    connection.close()