import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

from day2_agents.tools import emi_calculator

load_dotenv()

model = init_chat_model(os.environ["CHAT_MODEL"], reasoning=False, temperature=0)

agent = create_agent(
    model=model,
    tools=[emi_calculator],
    system_prompt=(
        "You are a careful loan assistant. "
        "Use tools for every calculation. Never guess numbers."
    ),
)

def label(message) -> str:
    if message.type == "human":
        return "HUMAN REQUEST"
    if message.type == "ai" and message.tool_calls:
        return "MODEL DECIDES TO CALL A TOOL"
    if message.type == "tool":
        return "TOOL RESULT"
    if message.type == "ai":
        return "FINAL ANSWER"
    return message.type.upper()

result = agent.invoke(
    {"messages": [{"role": "user", "content": "EMI for 5 lakh at 11% for 3 years?"}]},
    config={"run_name": "day2-lab3-loop", "tags": ["day2", "lab3"]},
)

for number, message in enumerate(result["messages"], start=1):
    print(f"\n[{number}] {label(message)}  ({type(message).__name__})")

    if message.type == "ai" and message.tool_calls:
        print(f"    text: {message.content!r}")
        for call in message.tool_calls:
            print(f"    wants: {call['name']}({call['args']})")
            print(f"    call id: {call['id']}")
    elif message.type == "tool":
        print(f"    tool: {message.name}")
        print(f"    answers call id: {message.tool_call_id}")
        print(f"    content: {message.content!r}")
    else:
        print(f"    content: {message.content}")
