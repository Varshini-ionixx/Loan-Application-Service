import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate

from day1_langchain.schema import LoanEnquiry

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


def read_enquiry(email: str) -> LoanEnquiry:
    """Read a customer's email and return the loan details found in it."""
    return chain.invoke({"email": email})


if __name__ == "__main__":
    print(read_enquiry("Hi, I'm Ramesh Kumar. I need a loan of 5 lakh rupees for 3 years to renovate my house."))
    print(read_enquiry("Hello, I am Priya. I would like a loan for a two-wheeler."))