from day3_rag.policy_index import build_index

store = build_index()
print("Chunks stored:", len(store.store))

for number, (chunk_id, record) in enumerate(store.store.items(), start=1):
    vector = record["vector"]
    print(f"\n--- chunk {number} ---")
    print("id      :", chunk_id)
    print("text    :", record["text"][:60].replace("\n", " "), "...")
    print("metadata:", record["metadata"])
    print("vector  :", len(vector), "numbers, first 5 =", [round(x, 3) for x in vector[:5]])