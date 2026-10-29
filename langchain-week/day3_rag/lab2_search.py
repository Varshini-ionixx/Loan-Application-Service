import os

from dotenv import load_dotenv
from langchain.embeddings import init_embeddings
from langchain_community.document_loaders import TextLoader
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

docs = TextLoader("data/loan_policy.txt", encoding="utf-8").load()
chunks = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50).split_documents(docs)

embeddings = init_embeddings(os.environ["EMBEDDING_MODEL"])

vector = embeddings.embed_query("How soon is the money paid out?")
print("Numbers in one embedding:", len(vector))
print("First 5 numbers        :", [round(x, 3) for x in vector[:5]])

store = InMemoryVectorStore.from_documents(chunks, embedding=embeddings)
print("\nChunks stored:", len(chunks))

QUESTIONS = [
    "How soon is the money paid out?",
    "Can I pay off my loan early?",
    "What ID do I need to show?",
    "Is there a penalty if I pay my EMI late?",
    "Do you offer gold loans?",
]

for question in QUESTIONS:
    top_chunk, top_score = store.similarity_search_with_score(question, k=1)[0]
    first_line = top_chunk.page_content.splitlines()[1] if "Section" in top_chunk.page_content else top_chunk.page_content.splitlines()[0]
    print(f"\n{question}\n  → score={top_score:.3f}  {first_line[:90]}")

print(f"\nQuestion: {question}")

for rank, (chunk, score) in enumerate(store.similarity_search_with_score(question, k=3), start=1):
    print(f"\n#{rank}  score={score:.3f}")
    print(chunk.page_content)
    print("---")