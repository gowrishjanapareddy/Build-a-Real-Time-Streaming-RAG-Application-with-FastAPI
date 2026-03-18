import os
import json
import asyncio
from fastapi import FastAPI, UploadFile, File, HTTPException
from dotenv import load_dotenv

load_dotenv()

# 1. Directory for shared file storage between App and Worker
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/app/data")
os.makedirs(UPLOAD_DIR, exist_ok=True)

try:
    import chainlit as cl
    from chainlit.utils import mount_chainlit
    CHAINLIT_AVAILABLE = True
except Exception:
    cl = None
    mount_chainlit = None
    CHAINLIT_AVAILABLE = False

# Import RAG engine
try:
    from app.engine import get_streaming_rag_response
    ENGINE_AVAILABLE = True
except Exception as e:
    ENGINE_AVAILABLE = False
    async def get_streaming_rag_response(*args, **kwargs):
        raise RuntimeError(f"Engine not available: {e}")

app = FastAPI()

# Redis connection
try:
    import redis.asyncio as redis
    redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379"), decode_responses=True)
    REDIS_AVAILABLE = True
except Exception:
    redis_client = None
    REDIS_AVAILABLE = False

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/ingest")
async def ingest_file(file: UploadFile = File(...)):
    if not REDIS_AVAILABLE or redis_client is None:
        raise HTTPException(status_code=503, detail="Redis connection unavailable.")

    # Validate file type
    ALLOWED_EXTENSIONS = {'.pdf', '.pptx', '.ppt', '.docx', '.doc', '.txt'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type: {file_ext}. Supported formats: PDF, PPTX, DOCX, TXT"
        )

    try:
        # Save the actual file to the shared volume
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Send the FILE PATH to the worker
        task = {
            "filename": file.filename,
            "file_path": file_path
        }

        # Match the queue name used in worker.py
        await redis_client.lpush("ingestion_queue", json.dumps(task))
        
        return {"message": f"Successfully queued {file.filename} for processing"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

# --- Chainlit Logic ---

if CHAINLIT_AVAILABLE:
    @cl.on_chat_start
    async def start():
        cl.user_session.set("history", [])
        await cl.Message(content="🚀 RAG System Online. Upload a document to begin!").send()

    @cl.on_message
    async def main_chat(message: cl.Message):
        # 1. Handle File Uploads via Chainlit UI
        if message.elements:
            ALLOWED_EXTENSIONS = {'.pdf', '.pptx', '.ppt', '.docx', '.doc', '.txt'}
            
            for element in message.elements:
                if element.type in ["file", "text"]:
                    # Validate file extension
                    file_ext = os.path.splitext(element.name)[1].lower()
                    if file_ext not in ALLOWED_EXTENSIONS:
                        await cl.Message(
                            content=f"⚠️ Unsupported file type: {file_ext}. Supported: PDF, PPTX, DOCX, TXT"
                        ).send()
                        continue
                    
                    try:
                        file_path = os.path.join(UPLOAD_DIR, element.name)
                        
                        # Handle content stored in memory or on disk
                        if element.content is not None:
                            content = element.content
                        elif element.path is not None and os.path.exists(element.path):
                            with open(element.path, "rb") as f:
                                content = f.read()
                        else:
                            await cl.Message(content=f"⚠️ Could not read {element.name}").send()
                            continue

                        # Write to shared volume
                        with open(file_path, "wb") as f:
                            f.write(content)
                        
                        # Trigger Worker Ingestion
                        task = {"filename": element.name, "file_path": file_path}
                        await redis_client.lpush("ingestion_queue", json.dumps(task))
                        await cl.Message(content=f"✅ `{element.name}` received. Indexing into ChromaDB...").send()
                    
                    except Exception as e:
                        await cl.Message(content=f"❌ Ingestion Error: {str(e)}").send()
                        # Trigger Worker Ingestion
                        task = {"filename": element.name, "file_path": file_path}
                        await redis_client.lpush("ingestion_queue", json.dumps(task))
                        await cl.Message(content=f"✅ `{element.name}` received. Indexing into ChromaDB...").send()
                    
                    except Exception as e:
                        await cl.Message(content=f"❌ Ingestion Error: {str(e)}").send()

        # 2. Handle Chat Response (RAG Retrieval + Generation)
        if message.content:
            msg = cl.Message(content="")
            try:
                async for token in get_streaming_rag_response(message.content):
                    await msg.stream_token(token)
                await msg.send()
            except Exception as e:
                await cl.Message(content=f"❌ Error generating response: {str(e)}").send()

# --- Mounting Logic ---

if CHAINLIT_AVAILABLE and not os.environ.get("CHAINLIT_RUN"):
    os.environ["CHAINLIT_RUN"] = "1"
    current_file_path = os.path.abspath(__file__)
    mount_chainlit(app, target=current_file_path, path="/")