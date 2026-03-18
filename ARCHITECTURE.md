graph TD
    %% Define Nodes and Subgraphs
    subgraph Client_Layer [Client Layer]
        User((User)) -->|Interact| UI[Chainlit UI]
    end

    subgraph API_Layer [API Layer - FastAPI]
        UI -->|Upload/Query| API[FastAPI Server]
        API -->|1. Save File| Disk[(Shared Volume: /app/data)]
        API -->|2. Push Task| Redis[(Redis Queue)]
        
        note1[<b>Decoupling:</b> Redis ensures<br/>API remains non-blocking]
        API -.-> note1
    end

    subgraph Background_Layer [Worker Layer]
        Redis -->|3. Pull Task| Worker[Ingestion Worker]
        Worker -->|4. Read/Chunk| Disk
        Worker -->|5. Embed| Ollama_E[Ollama: nomic-embed-text]
        Worker -->|6. Store| Chroma[(ChromaDB)]
        
        note2[<b>Shared Volume:</b> 'Bridge' for<br/>container file access]
        Disk -.-> note2
    end

    subgraph Inference_Layer [RAG Retrieval]
        API -->|7. Search| Chroma
        Chroma -->|8. Context| API
        API -->|9. Prompt| Ollama_G[Ollama: gemma3:4b]
        Ollama_G -->|10. Stream| UI
        
        note3[<b>Model:</b> Gemma 3:4b<br/>4GB RAM Optimized]
        Ollama_G -.-> note3
        
        note4[<b>Persistence:</b> ChromaDB mounted<br/>to local ./chroma_db]
        Chroma -.-> note4
    end

    %% Styling
    style note1 fill:#fff3cd,stroke:#ffeeba,stroke-width:1px
    style note2 fill:#fff3cd,stroke:#ffeeba,stroke-width:1px
    style note3 fill:#d1ecf1,stroke:#bee5eb,stroke-width:1px
    style note4 fill:#d4edda,stroke:#c3e6cb,stroke-width:1px
    style API fill:#f9f,stroke:#333,stroke-width:2px
    style Worker fill:#bbf,stroke:#333,stroke-width:2px
    
    
Decoupling via Redis: Using Redis as a message broker ensures that the FastAPI server remains non-blocking. Even if a user uploads a 50-page PDF, the chat interface stays responsive while the Worker handles the heavy lifting in the background.

Shared Volume Architecture: The /app/data volume is the "bridge" that allows the App container to save files and the Worker container to read them without duplicating data.

Persistent Vector Store: ChromaDB is mounted to a local directory (./chroma_db) so that your document embeddings are not lost if the Docker containers are restarted.

## Model Choice
Model: Gemma 3:4b.

Reasoning: This model provides a strong balance between reasoning capabilities and memory efficiency, requiring approximately 4.0 GiB of available system memory. This makes it ideal for local RAG deployments on consumer hardware.