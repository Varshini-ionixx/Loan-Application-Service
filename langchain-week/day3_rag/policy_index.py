import os

from dotenv import load_dotenv
from langchain.embeddings import init_embeddings
from langchain_community.document_loaders import TextLoader
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

POLICY_PATH = "data/loan_policy.txt"


def build_index(chunk_size: int = 300, chunk_overlap: int = 50) -> InMemoryVectorStore:
    """Load the loan policy, split it into chunks, embed them and return the vector store."""
    docs = TextLoader(POLICY_PATH, encoding="utf-8").load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.split_documents(docs)
    embeddings = init_embeddings(os.environ["EMBEDDING_MODEL"])
    return InMemoryVectorStore.from_documents(chunks, embedding=embeddings)
