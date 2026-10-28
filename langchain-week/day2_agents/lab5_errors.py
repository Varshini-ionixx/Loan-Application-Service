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
def strict_emi_calculator(principal: float, annual_rate_percent: float, tenure_months: int) -> float:
    """Calculate the monthly EMI of a loan.
    principal is in rupees, annual_rate_percent is like 11 for 11 percent,
    tenure_months is the loan length in months."""
    if tenure_months <= 0:
        raise ValueError("tenure_months must be positive")
    monthly_rate = annual_rate_percent / (12 * 100)
    growth = (1 + monthly_rate) ** tenure_months
    return round(principal * monthly_rate * growth / (growth - 1), 2)

BAD_INPUT = {"principal": 500000, "annual_rate_percent": 11, "tenure_months": -12}

print("=== Part A: direct calls ===")
try:
    strict_emi_calculator.invoke(BAD_INPUT)
except ValueError as error:
    print("Strict tool raised  :", type(error).__name__, "-", error)

print("Friendly tool returns:", emi_calculator.invoke(BAD_INPUT))

QUESTION = (
    "Use the EMI calculator for principal 500000, annual rate 11 percent "
    "and a tenure of -12 months."
)


def ask(title, chosen_tool):
    print(f"\n=== {title} ===")
    agent = create_agent(model=model, tools=[chosen_tool], system_prompt=SYSTEM)
    try:
        result = agent.invoke(
            {"messages": [{"role": "user", "content": QUESTION}]},
            config={"run_name": f"day2-lab5-{title}", "tags": ["day2", "lab5"]},
        )
    except Exception as error:
        print("AGENT CRASHED:", type(error).__name__, "-", error)
        return

    for message in result["messages"]:
        if message.type == "tool":
            print("Tool result :", message.content)
    print("Final answer:", result["messages"][-1].content)


ask("Part B - strict tool", strict_emi_calculator)
ask("Part C - friendly tool", emi_calculator)
