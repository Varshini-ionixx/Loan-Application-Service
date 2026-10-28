import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate

from schema import LoanEnquiry

load_dotenv()

model = init_chat_model(os.environ["CHAT_MODEL"], reasoning=False, temperature=0)
extractor = model.with_structured_output(LoanEnquiry, method="function_calling")

RULES = "..."  # copy the full RULES text from lab4_chain.py

prompt = ChatPromptTemplate.from_messages(
    [("system", RULES), ("human", "Customer email:\n{email}")]
)
chain = prompt | extractor

result = chain.invoke(
    {"email": "Dear sir, Suresh here. Business expansion loan, 25L, 5 years."},
    config={"run_name": "lab5-suresh", "tags": ["day1", "lab5"]},
)
print(result)
