from day3_rag.lab3_answer import model, prompt
from day3_rag.policy_index import build_index

QUESTION = "What are the charges if I prepay my loan?"

SETTINGS = [
    (80, 20),
    (300, 50),
    (2000, 50),
]

for chunk_size, chunk_overlap in SETTINGS:
    store = build_index(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = store.similarity_search(QUESTION, k=3)

    print(f"\n{'=' * 70}")
    print(f"chunk_size={chunk_size}, chunk_overlap={chunk_overlap}  →  total chunks in index: {len(store.store)}")

    for rank, chunk in enumerate(chunks, start=1):
        print(f"\n--- retrieved #{rank} ({len(chunk.page_content)} chars) ---")
        print(chunk.page_content)

    context = "\n\n---\n\n".join(chunk.page_content for chunk in chunks)
    answer = (prompt | model).invoke(
        {"context": context, "question": QUESTION},
        config={"run_name": f"day3-lab4-size{chunk_size}", "tags": ["day3", "lab4"]},
    )
    print("\nANSWER:", answer.content)
