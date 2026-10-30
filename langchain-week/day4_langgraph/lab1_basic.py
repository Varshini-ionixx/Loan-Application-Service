from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    text: str


def shout(state: State) -> dict:
    print("shout   received:", state)
    return {"text": state["text"].upper()}


def exclaim(state: State) -> dict:
    print("exclaim received:", state)
    return {"text": state["text"] + "!!!"}


builder = StateGraph(State)

builder.add_node("shout", shout)
builder.add_node("exclaim", exclaim)

builder.add_edge(START, "shout")
builder.add_edge("shout", "exclaim")
builder.add_edge("exclaim", END)

graph = builder.compile()

result = graph.invoke({"text": "hello loan desk"})
print("Final state:", result)