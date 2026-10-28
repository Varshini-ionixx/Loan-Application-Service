import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, SystemMessage

load_dotenv()

model = init_chat_model(os.environ["CHAT_MODEL"], reasoning=False, temperature=0)

def ask(system_prompt: str, question: str) -> str:
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=question),
    ]
    reply = model.invoke(messages)
    return reply.content

QUESTION = "What documents do I need to apply for a personal loan?"

FORMAL = (
    "You are a bank's loan officer. Reply formally and professionally, "
    "in at most 3 sentences."
)
CASUAL = (
    "You are a friendly helper texting a friend. Reply casually, "
    "use simple words, in at most 3 sentences."
)

print("=== FORMAL ===")
print(ask(FORMAL, QUESTION))

print("\n=== CASUAL ===")
print(ask(CASUAL, QUESTION))