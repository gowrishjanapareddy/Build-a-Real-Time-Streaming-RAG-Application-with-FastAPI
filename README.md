# Real-Time Streaming RAG Application with FastAPI

A production-ready, fully containerized **Retrieval-Augmented Generation (RAG)** application that delivers **token-by-token streaming responses** powered entirely by local LLMs via Ollama — no API keys, no cloud costs, complete data privacy.

> Upload any document → Ask questions → Watch AI answer in real-time, citing your document.

---

## Features

| Feature | Details |
|---------|---------|
| **Real-Time Streaming** | Responses stream token-by-token using FastAPI async generators |
| **Async Ingestion Pipeline** | Documents processed by a dedicated Redis-backed background worker |
| **Local LLM Inference** | Powered by Ollama (Gemma 3:4b + nomic-embed-text) |
| **Multi-Format Support** | PDF, DOCX, PPTX, TXT |
| **Persistent Vector Store** | ChromaDB with disk persistence across restarts |
| **Fully Containerized** | One-command startup with Docker Compose |
| **Chat UI** | Chainlit-powered interface integrated with FastAPI |
| **Source Citations** | Retrieval metadata surfaced during streaming |

---

## Technical Stack

| Layer | Technology |
|-------|-----------|
| **Frontend / UI** | [Chainlit](https://chainlit.io) (mounted on FastAPI) |
| **Backend API** | FastAPI (Python 3.11) + Uvicorn |
| **LLM** | Gemma 3:4b via Ollama |
| **Embeddings** | nomic-embed-text via Ollama |
| **Vector DB** | ChromaDB (persistent) |
| **Message Broker** | Redis (Alpine) |
| **Containerization** | Docker Compose |

---

## Prerequisites

- **Docker Desktop** (with Docker Compose) — [Install](https://docs.docker.com/get-docker/)
- **Ollama** installed on your host — [Install](https://ollama.com/)
- **Hardware**: ≥ 8 GB RAM (Gemma 3:4b needs ~4 GB)
- **OS**: Windows 10/11, macOS, or Linux

---

## Setup & Installation

### Step 1 — Pull Ollama Models (Host Machine)

```bash
ollama pull gemma3:4b
ollama pull nomic-embed-text
ollama list   # verify both models appear
```

### Step 2 — Clone the Repository

```bash
git clone https://github.com/gowrishjanapareddy/Build-a-Real-Time-Streaming-RAG-Application-with-FastAPI.git
cd Build-a-Real-Time-Streaming-RAG-Application-with-FastAPI
```

### Step 3 — Configure Environment

```bash
cp .env.example .env
```

The default `.env` values work out-of-the-box with Docker Compose. Edit only if you change model names or ports:

```env
REDIS_URL=redis://redis:6379
OLLAMA_BASE_URL=http://host.docker.internal:11434
EMBEDDING_MODEL=nomic-embed-text
LLM_MODEL=gemma3:4b
CHROMA_PERSIST_DIR=./chroma_db
UPLOAD_DIR=/app/data
```

> **Windows / WSL note:** `host.docker.internal` is automatically resolved by Docker Desktop. On Linux, Docker Compose adds it via `extra_hosts`.

### Step 4 — Build & Start All Services

```bash
docker-compose up --build
```

This starts three services: **redis**, **app** (FastAPI + Chainlit), **worker** (ingestion).

---

## Running the Application

| Endpoint | URL |
|----------|-----|
| **Chat UI** | http://localhost:8000 |
| **Health Check** | http://localhost:8000/health |
| **File Ingest API** | `POST http://localhost:8000/ingest` |

### Using the Chat Interface

1. Open **http://localhost:8000** in your browser
2. Click the **📎 upload button** to attach a document (PDF, DOCX, PPTX, or TXT)
3. The system will respond: *"Indexing into ChromaDB..."*
4. Once indexed, type any question related to the document
5. Watch the response **stream in real-time**, token by token

### Using the REST API (Programmatic Ingestion)

```bash
curl -X POST http://localhost:8000/ingest \
  -F "file=@/path/to/your/document.pdf"
```

---

## Running Tests

### Local tests (requires Python venv)

```bash
cd backend
python -m pytest ../tests/ -v
```

### Via Docker

```bash
docker-compose exec app pytest /tests/ -v
```

---

## Stopping the Application

```bash
docker-compose down          # stop containers
docker-compose down -v       # stop + remove volumes (clears ChromaDB)
```

---

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app + Chainlit UI + /ingest endpoint
│   │   ├── engine.py        # RAG retrieval engine (streaming)
│   │   └── worker.py        # Redis-backed async document ingestion worker
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── test_retrieval.py    # Manual retrieval smoke test
│   └── verify_env.py        # Environment variable verification
├── frontend/                # Custom frontend assets
├── tests/
│   └── test_main.py         # Pytest integration tests
├── docker-compose.yml
├── .env.example             # Safe environment template
├── submission.yml
├── README.md
├── ARCHITECTURE.md
└── BENCHMARKS.md
```

---

## How It Works

1. **Upload**: User uploads a document via Chainlit UI or `/ingest` REST API
2. **Queue**: FastAPI saves the file to a shared Docker volume and pushes a task to Redis
3. **Ingest**: Worker pulls the task, loads the document, splits into chunks, embeds with `nomic-embed-text`, stores in ChromaDB
4. **Query**: User sends a chat message → FastAPI retrieves top-k similar chunks from ChromaDB
5. **Stream**: Retrieved context + query sent to Gemma 3:4b → response streamed token-by-token back to the UI

---

## Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -m 'Add my feature'`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request

MIT License — see [LICENSE](LICENSE) for details.
