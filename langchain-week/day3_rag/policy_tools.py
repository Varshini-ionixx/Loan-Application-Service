from langchain.tools import tool

from day3_rag.policy_index import build_index

store = build_index()


@tool
def search_policy(query: str) -> str:
    """Search the bank's loan policy document.
    Use this for any question about the policy: eligibility rules, loan amount and
    tenure limits, interest rates, processing fees, prepayment and late payment
    charges, required documents, approvals and disbursal.
    Returns the most relevant policy extracts. Each rule starts with its section number."""
    chunks = store.similarity_search(query, k=3)
    return "\n\n---\n\n".join(chunk.page_content for chunk in chunks)