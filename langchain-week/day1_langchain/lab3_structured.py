import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

from schema import LoanEnquiry

load_dotenv()

model = init_chat_model(os.environ["CHAT_MODEL"], reasoning=False, temperature=0)
extractor = model.with_structured_output(LoanEnquiry)

email = (
    "Hi, I'm Ramesh Kumar. I need a loan of 5 lakh rupees for 3 years "
    "to renovate my house. Please let me know the process."
)

from langchain.messages import HumanMessage, SystemMessage

RULES = (
    "Extract loan enquiry details from the customer's email. "
    "Only use information that is explicitly stated. "
    "If a value is not stated, return null for it. Never guess. "
    "1 lakh = 100000 rupees. Convert years to months."
)

result = extractor.invoke([SystemMessage(content=RULES), HumanMessage(content=email)])


print("Type:", type(result).__name__)
print(result)
print("Amount:", result.amount)
print("Tenure:", result.tenure_months)
print("As a dict:", result.model_dump())
