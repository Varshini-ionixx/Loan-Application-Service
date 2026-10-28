from dotenv import load_dotenv

load_dotenv()

from loan_api_client.client import LoanApiClient

api = LoanApiClient()
print("Customer 4   :", api.get_customer(4))
print("Customer 5:", api.get_customer(5))