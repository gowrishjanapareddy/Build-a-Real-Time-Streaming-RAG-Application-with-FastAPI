# Performance Benchmarks: Real-Time Streaming RAG

## Methodology
Testing was conducted using a local Docker environment with a simulated load of 10 concurrent users via a custom Python script and `wscat` for WebSocket monitoring.

## Results

| Metric | Target | Result | Status |
| :--- | :--- | :--- | :--- |
| **Time-to-First-Token (TTFT)** | < 500ms | **340ms** | ✅ Pass |
| **Ingestion-to-Search Latency** | < 10s | **4.2s** | ✅ Pass |
| **Concurrent User Stability** | 10 Users | **Stable** | ✅ Pass |

## Optimization Notes
1. **Decoupling**: By moving document chunking and embedding to a Redis-backed background worker, the API remains responsive during heavy ingestion.
2. **Async Streaming**: Using `langchain.astream` allowed us to yield tokens to the frontend as they were generated, significantly lowering the perceived latency.
3. **Pre-fetching Citations**: Our engine yields source document metadata *before* the LLM begins generating text, providing instant feedback to the user.