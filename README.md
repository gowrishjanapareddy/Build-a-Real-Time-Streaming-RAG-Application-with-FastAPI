## Real-Time Streaming RAG Application ##

This project is a high-performance, containerized Retrieval-Augmented Generation (RAG) application. It allows users to upload documents (PDF, DOCX) and engage in a real-time, streaming chat powered by Gemma 3:4b. The architecture is decoupled using a background worker and Redis to ensure the UI remains responsive during heavy document ingestion.

## Features 
Real-Time Streaming: Responses are delivered token-by-token using FastAPI asynchronous generators.

Asynchronous Ingestion: Document processing (chunking and embedding) is handled by a dedicated worker service.

Local Inference: Powered by Ollama, ensuring data privacy and no API costs.

Multi-Format Support: Supports PDF and DOCX files.

Persistent Vector Store: Uses ChromaDB to store embeddings across sessions.

## Technical Stack
Frontend: Chainlit (Integrated via FastAPI)

Backend: FastAPI (Python 3.11)

LLM: Gemma 3:4b (via Ollama)

Embeddings: nomic-embed-text

Database: ChromaDB

Broker: Redis

## Prerequisites
Docker & Docker Compose installed.

Ollama installed on the host machine.

Hardware: At least 8GB of RAM (Gemma 3:4b requires ~4.0 GiB of available system memory).

## Setup & Installation

1. Pull Required Models
On your host machine, run:
Bash
ollama pull gemma3:4b
ollama pull nomic-embed-text

2. Clone the Repository
Bash
git clone <https://github.com/Harshitha-teki/Build-a-Real-Time-Streaming-RAG-Application-with-FastAPI.git>
cd <project-folder>

3. Environment Configuration
Ensure host.docker.internal is accessible in your environment to allow Docker containers to communicate with the Ollama service on your host.

4. Build and Run
Bash
docker-compose up --build -d

## Running the Application
UI Access: Open http://localhost:8000 in your browser.

API Health Check: http://localhost:8000/health.

## Usage Instructions
Chat: Type a message to interact with the LLM directly.

Ingest: Use the upload button in the UI or send a POST request to /ingest.

Query: Once the UI confirms "Indexing complete," ask questions related to your document. The system will provide answers with source citations.

## Usage Instructions
Chat: Type a message to interact with the LLM directly.

Ingest: Use the upload button in the UI or send a POST request to /ingest.

Query: Once the UI confirms "Indexing complete," ask questions related to your document. The system will provide answers with source citations.

