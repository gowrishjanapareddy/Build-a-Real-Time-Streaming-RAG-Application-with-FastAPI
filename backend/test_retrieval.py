import asyncio
import os
from dotenv import load_dotenv

# Load .env from the root directory
load_dotenv(dotenv_path="../.env")

# Mock the imports used in engine.py
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_chroma import Chroma

# 1. Use local embeddings
embeddings = OllamaEmbeddings(
    model=os.getenv("EMBEDDING_MODEL", "nomic-embed-text"), 
    base_url=os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
)

# Use absolute path for ChromaDB to be sure
db_path = os.path.join(os.getcwd(), "chroma_db")
print(f"Checking ChromaDB at: {db_path}")

try:
    vectorstore = Chroma(persist_directory=db_path, embedding_function=embeddings)
    all_docs = vectorstore.similarity_search("sql", k=5)
    print(f"Number of documents found: {len(all_docs)}")
    for doc in all_docs:
        print(f"- Source: {doc.metadata.get('source')} - Content length: {len(doc.page_content)}")
except Exception as e:
    print(f"Error during retrieval test: {str(e)}")
    import traceback
    traceback.print_exc()
