import os
import sys

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

from day2_agents.tools import emi_calculator
from day3_rag.policy_tools import search_policy

model = init_chat_model(os.environ["CHAT_MODEL"], reasoning=False, temperature=0)

SYSTEM_PROMPT = (
    "You are a careful loan assistant. Use tools for every calculation. Never guess numbers.\n"
    "For questions about the loan policy, call search_policy and answer only from its results. "
    "End policy answers with the section numbers you used, like: Sources: [3.2]\n"
    "If the search results do not contain the answer, say: I could not find this in the policy."
)

agent = create_agent(
    model=model,
    tools=[search_policy, emi_calculator],
    system_prompt=SYSTEM_PROMPT,
)

QUESTIONS = {
    1: "What documents does a salaried applicant need?",
    2: "What is the EMI for 5 lakh at 11% for 3 years?",
    3: "I want 6,00,000 for 36 months at 11%. What is the EMI and the processing fee?",
    4: "What is the policy on gold loans?",
}


def ask(number: int, question: str) -> None:
    result = agent.invoke(
        {"messages": [{"role": "user", "content": question}]},
        config={"run_name": f"day3-lab5-q{number}", "tags": ["day3", "lab5"]},
    )
    calls = [call for m in result["messages"] for call in (getattr(m, "tool_calls", None) or [])]

    print(f"\n=== Q{number}: {question}")
    print("Tool order:", " -> ".join(call["name"] for call in calls) if calls else "no tools called")
    for call in calls:
        print(f"   {call['name']}({call['args']})")
    print("Answer:", result["messages"][-1].content)


chosen = [int(arg) for arg in sys.argv[1:]] or list(QUESTIONS)
for number in chosen:
    ask(number, QUESTIONS[number])