import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

model = init_chat_model(os.environ["CHAT_MODEL"], reasoning=False, temperature=0)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a loan desk assistant. Read the customer's email and reply "
            "with ONE short sentence saying what they want. Do not add advice.",
        ),
        ("human", "Customer email:\n{email}"),
    ]
)

print("Variables:", prompt.input_variables)

preview = prompt.invoke({"email": "Test email text"})
for message in preview.to_messages():
    print(f"[{message.type}] {message.content}")

EMAILS = [
    "Hi, I'm Ramesh Kumar. I need a loan of 5 lakh rupees for 3 years to renovate my house. Please let me know the process.",
    "need money urgently for my shop, around 2 lakhs, can repay in 18 months. - Imran",
    "Good morning, I want to know if I can get a loan for buying a two-wheeler. My name is Priya.",
]

for email in EMAILS:
    prompt_value = prompt.invoke({"email": email})
    reply = model.invoke(prompt_value)
    print("\nEMAIL:", email)
    print("MODEL:", reply.content)
