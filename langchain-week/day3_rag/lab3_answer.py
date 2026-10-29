import os

from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate

from day3_rag.policy_index import build_index

model = init_chat_model(os.environ["CHAT_MODEL"], reasoning=False, temperature=0)
store = build_index()

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You answer questions about the bank's loan policy.\n"
            "Use ONLY the policy extracts in the context below. Do not use outside knowledge.\n"
            "Each rule starts with its section number, like 3.3.\n"
            "After your answer, cite every section number you used in square brackets, like [3.3].\n"
            "If the context does not contain the answer, reply exactly: "
            "I could not find this in the policy.\n"
            "Never invent numbers that are not in the context.\n"
            "Reply in plain text, without markdown.",
        ),
        ("human", "Context:\n{context}\n\nQuestion: {question}"),
    ]
)

def ask(question: str) -> str:
    chunks = store.similarity_search(question, k=3)
    context = "\n\n---\n\n".join(chunk.page_content for chunk in chunks)

    print(f"\nQUESTION: {question}")
    print("Retrieved:", [chunk.page_content.splitlines()[-1][:40] for chunk in chunks])

    answer = (prompt | model).invoke(
        {"context": context, "question": question},
        config={"run_name": "day3-lab3-ask", "tags": ["day3", "lab3"]},
    )
    print("ANSWER  :", answer.content)
    return answer.content

if __name__ == "__main__":
    ask("What is the minimum age to apply?")
    ask("How long until the loan amount is disbursed?")
    ask("Can I prepay my loan after 8 months?")
    ask("What is the policy on gold loans?")