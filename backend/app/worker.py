import json
import asyncio
import redis.asyncio as redis
import os
from dotenv import load_dotenv

load_dotenv()
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.document_loaders import UnstructuredPowerPointLoader, UnstructuredWordDocumentLoader
from langchain_core.documents import Document

async def load_document(file_path):
    """
    Load documents based on file type.
    Supports: PDF, PPTX, DOCX, TXT
    """
    file_ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if file_ext == '.pdf':
            loader = PyPDFLoader(file_path)
            documents = loader.load()
        elif file_ext in ['.pptx', '.ppt']:
            loader = UnstructuredPowerPointLoader(file_path)
            documents = loader.load()
        elif file_ext in ['.docx', '.doc']:
            loader = UnstructuredWordDocumentLoader(file_path)
            documents = loader.load()
        elif file_ext in ['.txt']:
            loader = TextLoader(file_path)
            documents = loader.load()
        else:
            # Fallback: try UnstructuredLoader for other formats
            from langchain_community.document_loaders import UnstructuredFileLoader
            loader = UnstructuredFileLoader(file_path)
            documents = loader.load()
        
        return documents
    except Exception as e:
        print(f"Error loading {file_ext} file: {e}")
        raise

async def process_queue():
    r = redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379"), decode_responses=True)
    
    # Use llama3.2:1b for the LLM, but nomic-embed-text is fine for embeddings 
    # as long as you have pulled it: ollama pull nomic-embed-text
    embeddings = OllamaEmbeddings(
        model=os.getenv("EMBEDDING_MODEL", "nomic-embed-text"), 
        base_url=os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
    )
    vectorstore = Chroma(persist_directory=os.getenv("CHROMA_PERSIST_DIR", "./chroma_db"), embedding_function=embeddings)
    
    print("Worker started. Listening for tasks...")
    while True:
        try:
            _, message = await r.brpop("ingestion_queue")
            data = json.loads(message)
            file_path = data.get('file_path')
            filename = data.get('filename')
            
            if not file_path or not os.path.exists(file_path):
                print(f"Error: File path {file_path} not found.")
                continue

            print(f"Processing file: {filename}")

            # STEP 1: LOAD THE DOCUMENT
            documents = await load_document(file_path)
            
            # STEP 2: ADD SOURCE FILENAME TO METADATA
            for doc in documents:
                if doc.metadata is None:
                    doc.metadata = {}
                doc.metadata["source"] = filename

            # STEP 3: SPLIT THE TEXT
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            chunks = splitter.split_documents(documents)
            
            # STEP 4: ADD TO VECTOR STORE
            vectorstore.add_documents(chunks)
            
            print(f"✅ Successfully indexed {len(chunks)} chunks from: {filename}")
            
        except Exception as e:
            print(f"❌ Worker Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(process_queue())