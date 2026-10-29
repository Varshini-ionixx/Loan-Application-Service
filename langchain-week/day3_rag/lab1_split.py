from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

docs = TextLoader("data/loan_policy.txt", encoding="utf-8").load()

print("Documents loaded:", len(docs))
print("Characters      :", len(docs[0].page_content))
print("Metadata        :", docs[0].metadata)

splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
chunks = splitter.split_documents(docs)

print("\nChunks:", len(chunks))
for number, chunk in enumerate(chunks, start=1):
    print(f"\n--- chunk {number} ({len(chunk.page_content)} chars) ---")
    print(chunk.page_content)