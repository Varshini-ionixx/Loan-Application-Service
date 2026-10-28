import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool

from day2_agents.tools import emi_calculator

load_dotenv()

model = init_chat_model(os.environ["CHAT_MODEL"], reasoning=False, temperature=0)

SYSTEM = (
    "You are a careful loan assistant. "
    "Use tools for every calculation. Never guess numbers."
)

@tool("emi_calculator")
def vague_emi_calculator(principal: float, annual_rate_percent: float, tenure_months: int) -> float:
    """does maths"""
    monthly_rate = annual_rate_percent / (12 * 100)
    growth = (1 + monthly_rate) ** tenure_months
    return round(principal * monthly_rate * growth / (growth - 1), 2)

@tool
def calc(a: float, b: float, c: int) -> float:
    """does maths"""
    monthly_rate = b / (12 * 100)
    growth = (1 + monthly_rate) ** c
    return round(a * monthly_rate * growth / (growth - 1), 2)

QUESTION = "Over 18 months at 9.5% interest, what is the monthly payment on a 2 lakh loan?"


def run(title, chosen_tool):
    agent = create_agent(model=model, tools=[chosen_tool], system_prompt=SYSTEM)
    result = agent.invoke(
        {"messages": [{"role": "user", "content": QUESTION}]},
        config={"run_name": f"day2-lab4-{title}", "tags": ["day2", "lab4"]},
    )

    print(f"\n=== {title} ===")
    print("Model sees:", chosen_tool.name, "-", chosen_tool.description.splitlines()[0])

    calls = [call for m in result["messages"] for call in (getattr(m, "tool_calls", None) or [])]
    if not calls:
        print("Tool calls: NONE (the model answered without using the tool)")
    for call in calls:
        print(f"Tool call : {call['name']}({call['args']})")

    print("Answer    :", result["messages"][-1].content)


run("good-docstring", emi_calculator)
run("vague-docstring", vague_emi_calculator)
run("vague-everything", calc)