from day2_agents.tools import emi_calculator

print("Name       :", emi_calculator.name)
print("Description:", emi_calculator.description)
print("Args       :", emi_calculator.args)

emi2 = emi_calculator.invoke(
    {"principal": 300000, "annual_rate_percent": 10.5, "tenure_months": 24}
)
print(f"EMI for 3,00,000 at 10.5% for 24 months: {emi2:,.2f}")