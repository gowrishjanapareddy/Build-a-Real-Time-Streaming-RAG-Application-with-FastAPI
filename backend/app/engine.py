import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_chroma import Chroma
from datetime import datetime

# 1. Use local embeddings (Free & Fast)
embeddings = OllamaEmbeddings(
    model=os.getenv("EMBEDDING_MODEL", "nomic-embed-text"), 
    base_url=os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
)
# 2. Use local LLM (Free & No Quota limits)
llm = ChatOllama(
    model=os.getenv("LLM_MODEL", "llama3.2:1b"), 
    base_url=os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
)
vectorstore = Chroma(persist_directory=os.getenv("CHROMA_PERSIST_DIR", "./chroma_db"), embedding_function=embeddings)

async def get_streaming_rag_response(query):
    # Search the local database with metadata filtering
    try:
        # Get all documents and find the most recent one by source
        all_docs = await asyncio.to_thread(vectorstore.similarity_search, query, k=20)
        
        if not all_docs:
            yield "No documents found in the database."
            return
        
        # Group docs by source (filename)
        docs_by_source = {}
        for doc in all_docs:
            source = doc.metadata.get("source", "unknown")
            if source not in docs_by_source:
                docs_by_source[source] = []
            docs_by_source[source].append(doc)
        
        # Get the most recent source (last one added)
        # For now, use the last source in the dict (most recent upload)
        most_recent_source = list(docs_by_source.keys())[-1] if docs_by_source else None
        
        # Prioritize docs from most recent source, fall back to others
        selected_docs = docs_by_source.get(most_recent_source, [])[:3]
        
        # If we have fewer than 3 docs from recent source, add from other sources
        if len(selected_docs) < 3:
            other_docs = [d for source in docs_by_source.keys() 
                         for d in docs_by_source[source] 
                         if source != most_recent_source]
            selected_docs.extend(other_docs[:3 - len(selected_docs)])
        
        context = "\n".join([d.page_content for d in selected_docs[:3]])
        
        prompt = f"Context: {context}\n\nQuestion: {query}\n\nAnswer:"
        
        # Stream from your local machine
        async for chunk in llm.astream(prompt):
            yield chunk.content
    except Exception as e:
        yield f"Error retrieving documents: {str(e)}"