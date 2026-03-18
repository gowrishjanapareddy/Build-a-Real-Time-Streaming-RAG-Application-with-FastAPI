import os
from dotenv import load_dotenv

# Load .env from the root directory
load_dotenv(dotenv_path="../.env")

print(f"REDIS_URL: {os.getenv('REDIS_URL')}")
print(f"OLLAMA_BASE_URL: {os.getenv('OLLAMA_BASE_URL')}")
print(f"EMBEDDING_MODEL: {os.getenv('EMBEDDING_MODEL')}")
print(f"LLM_MODEL: {os.getenv('LLM_MODEL')}")
print(f"CHROMA_PERSIST_DIR: {os.getenv('CHROMA_PERSIST_DIR')}")
print(f"UPLOAD_DIR: {os.getenv('UPLOAD_DIR')}")
