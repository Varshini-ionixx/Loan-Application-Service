import os
import sys

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

from day2_agents.tools import check_eligibility, emi_calculator, get_customer

load_dotenv()

model = init_chat_model(os.environ["CHAT_MODEL"], reasoning=False, temperature=0)

SYSTEM_PROMPT = """You are a careful loan assistant for a bank.

Rules:
- Use the tools for every number. Never calculate or guess numbers yourself.
- To check if a customer is eligible for a loan, use the tools in this order:
  1. get_customer to fetch the customer's details,
  2. emi_calculator for the requested loan,
  3. check_eligibility with the customer's details and the new EMI.
- If get_customer says the customer is not found or the profile is incomplete,
  tell the user that. Do not invent any details.
- If the user has not given the details a tool needs (customer ID, loan amount,
  interest rate or tenure), ask for them. Never call a tool with guessed values.
- When a customer is not eligible, list every failed rule.
- Only help with loans, EMIs and eligibility. Politely decline anything else.
- Reply in plain text, without markdown."""

agent = create_agent(
    model=model,
    tools=[get_customer, emi_calculator, check_eligibility],
    system_prompt=SYSTEM_PROMPT,
)

TEST_QUESTIONS = {
    1: "EMI for 3,00,000 at 10.5% for 24 months?",
    2: "Is customer 4 eligible for 5,00,000 at 11% for 36 months?",
    3: "Is customer 5 eligible for 4,00,000 at 11% for 24 months?",
    4: "Is customer 9999 eligible for a loan?",
    5: "What is the capital of France?",
    6: "Can I get a loan?",
}

def ask(number: int, question: str) -> None:
    result = agent.invoke(
        {"messages": [{"role": "user", "content": question}]},
        config={"run_name": f"day2-agent-q{number}", "tags": ["day2", "agent"]},
    )

    calls = [call for m in result["messages"] for call in (getattr(m, "tool_calls", None) or [])]

    print(f"\n=== Q{number}: {question}")
    print("Tool order:", " -> ".join(call["name"] for call in calls) if calls else "no tools called")
    for call in calls:
        print(f"   {call['name']}({call['args']})")
    print("Answer:", result["messages"][-1].content)


chosen = [int(arg) for arg in sys.argv[1:]] or list(TEST_QUESTIONS)
for number in chosen:
    ask(number, TEST_QUESTIONS[number])