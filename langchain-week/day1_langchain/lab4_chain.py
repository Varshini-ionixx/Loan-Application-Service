import os
import time

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate

from schema import LoanEnquiry

load_dotenv()

model = init_chat_model(os.environ["CHAT_MODEL"], reasoning=False, temperature=0)
extractor = model.with_structured_output(LoanEnquiry, method="function_calling")

RULES = (
    "You extract loan enquiry details from a customer's email into these fields:\n"
    "- customer_name: the person's name as written, or null\n"
    "- amount: the loan amount as a plain number of rupees, or null\n"
    "- tenure_months: the repayment period as a whole number of months, or null\n"
    "- purpose: why they need the loan, in at most 5 words, or null\n"
    "Rules:\n"
    "- Converting units is NOT guessing. Always convert:\n"
    "  '5 lakh' = 500000, '2 lakhs' = 200000, '25L' = 2500000, "
    "'Rs 12,00,000' = 1200000 (Indian digit grouping), '3 years' = 36, '5 years' = 60.\n"
    "- Approximate amounts like 'around 2 lakhs' still count: use 200000.\n"
    "- If a value is not mentioned at all, return null. Never invent values.\n"
    "- Only fill the fields. Do not explain your reasoning."
)


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", RULES),
        ("human", "Customer email:\n{email}"),
    ]
)

chain = prompt | extractor

one = chain.invoke({"email": "Hi, I'm Ramesh Kumar. I need a loan of 5 lakh rupees for 3 years to renovate my house."})
print("Single:", one)

EMAILS = [
    "Hello team, this is Anita Sharma. Looking for Rs 12,00,000 personal loan, repayment over 60 months, for my sister's wedding.",
    "need money urgently for my shop, around 2 lakhs, can repay in 18 months. - Imran",
    "Dear sir, Suresh here. Business expansion loan, 25L, 5 years. Also what are your interest rates?",
]

inputs = [{"email": email} for email in EMAILS]

start = time.perf_counter()
results = chain.batch(inputs)
seconds = time.perf_counter() - start

print(f"\nBatch of {len(results)} took {seconds:.1f}s")
for email, result in zip(EMAILS, results):
    print("\nEMAIL :", email)
    print("RESULT:", type(result).__name__, result.model_dump())

print("\n\nStreaming:")
for chunk in model.stream("Explain what an EMI is in 3 short sentences."):
    print(chunk.content, end="", flush=True)
print()
