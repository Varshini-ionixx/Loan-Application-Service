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

result = agent.invoke(
    {"messages": [{"role": "user", "content": "EMI for 5 lakh at 11% for 3 years?"}]},
    config={"run_name": "day2-lab2-emi", "tags": ["day2", "lab2"]},
)

print(result["messages"][-1].content)

print("\nTool calls made:")
for message in result["messages"]:
    for call in getattr(message, "tool_calls", []) or []:
        print(f"  {call['name']}({call['args']})")
