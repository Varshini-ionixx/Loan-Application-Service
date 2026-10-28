from day2_agents.tools import check_eligibility, emi_calculator, get_customer

print("Customer 4   :", get_customer.invoke({"customer_id": 4}))
print("Customer 5   :", get_customer.invoke({"customer_id": 5}))
print("Customer 9999:", get_customer.invoke({"customer_id": 9999}))

emi_4 = emi_calculator.invoke({"principal": 500000, "annual_rate_percent": 11, "tenure_months": 36})
print("\nCustomer 4, 5L at 11% for 36 months, EMI:", emi_4)
print(check_eligibility.invoke(
    {"age": 38, "monthly_income": 85000, "existing_emi": 12000, "credit_score": 745, "new_emi": emi_4}
))

emi_5 = emi_calculator.invoke({"principal": 400000, "annual_rate_percent": 11, "tenure_months": 24})
print("\nCustomer 5, 4L at 11% for 24 months, EMI:", emi_5)
print(check_eligibility.invoke(
    {"age": 52, "monthly_income": 40000, "existing_emi": 22000, "credit_score": 680, "new_emi": emi_5}
))
