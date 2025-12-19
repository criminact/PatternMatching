## Semantic Product Retrieval (Images + Gemini + Chroma)

This prototype ingests multiple product images, lets Gemini draft a unified description, and stores a semantic embedding in ChromaDB with rich metadata (name, image URLs, keywords). Queries can be keyword or natural language; results return product details and image references.

### System Architecture

```mermaid
graph TB
    subgraph "Frontend (Next.js)"
        UI[User Interface]
        IngestPage[Ingest Page]
        SearchPage[Search Page]
    end
    
    subgraph "Backend API (FastAPI)"
        API[FastAPI Server]
        IngestEP[POST /ingest]
        SearchEP[POST /search]
        GenDescEP[POST /generate_description]
    end
    
    subgraph "AI Services"
        Gemini[Gemini 2.5 Flash]
        Embeddings[sentence-transformers<br/>all-MiniLM-L6-v2]
    end
    
    subgraph "Vector Database"
        ChromaDB[(ChromaDB)]
        Collection[Product Collection]
    end
    
    UI --> IngestPage
    UI --> SearchPage
    
    IngestPage -->|1. Submit Product| GenDescEP
    GenDescEP -->|2. Fetch Images| ImageURLs[Image URLs]
    GenDescEP -->|3. Process Each Image| Gemini
    Gemini -->|4. Individual Descriptions| GenDescEP
    GenDescEP -->|5. Collate Descriptions| Gemini
    Gemini -->|6. Final Description| GenDescEP
    GenDescEP -->|7. Return Description| IngestPage
    IngestPage -->|8. Submit with Description| IngestEP
    IngestEP -->|9. Generate Embedding| Embeddings
    Embeddings -->|10. Store Vector + Metadata| ChromaDB
    ChromaDB --> Collection
    
    SearchPage -->|1. Submit Query| SearchEP
    SearchEP -->|2. Generate Query Embedding| Embeddings
    Embeddings -->|3. Semantic Search| ChromaDB
    ChromaDB -->|4. Return Similar Products| SearchEP
    SearchEP -->|5. Return Results| SearchPage
```

### Ingestion Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant Gemini
    participant ChromaDB
    
    User->>Frontend: Enter product details<br/>(name, keywords, image URLs)
    Frontend->>API: POST /generate_description
    API->>Gemini: Process Image 1<br/>(Generate visual description)
    Gemini-->>API: Description 1
    API->>Gemini: Process Image 2<br/>(Generate visual description)
    Gemini-->>API: Description 2
    API->>Gemini: Process Image N<br/>(Generate visual description)
    Gemini-->>API: Description N
    API->>Gemini: Collate all descriptions<br/>(Create unified description)
    Gemini-->>API: Final comprehensive description
    API-->>Frontend: Return description
    Frontend->>User: Display editable description
    User->>Frontend: Review/edit description
    Frontend->>API: POST /ingest<br/>(name, keywords, image_urls, description)
    API->>API: Generate embedding from description
    API->>ChromaDB: Store vector + metadata<br/>(name, keywords, image_urls, description)
    ChromaDB-->>API: Confirmation
    API-->>Frontend: Product ID + stored data
    Frontend->>User: Success message
```

### Search Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant Embeddings
    participant ChromaDB
    
    User->>Frontend: Enter search query<br/>(natural language or keywords)
    Frontend->>API: POST /search<br/>(query, top_k)
    API->>Embeddings: Generate query embedding
    Embeddings-->>API: Query vector
    API->>ChromaDB: Semantic similarity search<br/>(query vector, top_k)
    ChromaDB->>ChromaDB: Find similar vectors
    ChromaDB-->>API: Results with scores<br/>(product_id, distance, metadata)
    API->>API: Parse JSON metadata<br/>(keywords, image_urls)
    API->>API: Convert distance to similarity score
    API-->>Frontend: Search results<br/>(products with scores)
    Frontend->>User: Display matching products<br/>(images, description, keywords)
```

### Data Flow

```mermaid
graph LR
    subgraph "Input"
        Images[Product Images<br/>Multiple URLs]
        Name[Product Name]
        Keywords[Keywords List]
    end
    
    subgraph "Processing"
        GeminiDesc[Gemini AI<br/>Visual Description<br/>Generation]
        Embedding[Text Embedding<br/>Vector Generation]
    end
    
    subgraph "Storage"
        Vector[Vector Embedding<br/>768 dimensions]
        Metadata[Metadata<br/>name, keywords,<br/>image_urls, description]
    end
    
    subgraph "Retrieval"
        Query[User Query<br/>Natural Language]
        Search[Semantic Search<br/>Cosine Similarity]
        Results[Ranked Results<br/>with Scores]
    end
    
    Images --> GeminiDesc
    Name --> GeminiDesc
    Keywords --> GeminiDesc
    GeminiDesc --> Description[Rich Visual Description]
    Description --> Embedding
    Embedding --> Vector
    Name --> Metadata
    Keywords --> Metadata
    Images --> Metadata
    Description --> Metadata
    
    Vector --> ChromaDB[(ChromaDB)]
    Metadata --> ChromaDB
    
    Query --> Embedding
    Embedding --> Search
    Search --> ChromaDB
    ChromaDB --> Results
```

### Component Details

```mermaid
graph TB
    subgraph "Frontend Components"
        HomePage[Home Page<br/>Landing & Navigation]
        IngestPage[Ingest Page<br/>Product Upload Form]
        SearchPage[Search Page<br/>Query Interface]
    end
    
    subgraph "Backend Services"
        AppPy[app.py<br/>FastAPI Routes]
        Ingestion[ingestion.py<br/>Product Storage]
        Search[search.py<br/>Semantic Search]
        GeminiClient[gemini_client.py<br/>AI Description Generation]
        VectorStore[vector_store.py<br/>ChromaDB Client]
    end
    
    subgraph "External Services"
        GeminiAPI[Google Gemini API<br/>Image Analysis]
        ChromaDB[(ChromaDB<br/>Vector Database)]
    end
    
    HomePage --> IngestPage
    HomePage --> SearchPage
    IngestPage --> AppPy
    SearchPage --> AppPy
    AppPy --> Ingestion
    AppPy --> Search
    AppPy --> GeminiClient
    Ingestion --> VectorStore
    Search --> VectorStore
    GeminiClient --> GeminiAPI
    VectorStore --> ChromaDB
```

### Quickstart
- Create a virtual environment and install deps:
  - `python -m venv .venv && source .venv/bin/activate`
  - `pip install -r requirements.txt`
- Set environment variables:
  
  **GEMINI_API_KEY** (Required):
  - Linux/Mac: `export GEMINI_API_KEY="your-api-key-here"`
  - Windows (PowerShell): `$env:GEMINI_API_KEY="your-api-key-here"`
  - Windows (CMD): `set GEMINI_API_KEY=your-api-key-here`
  - Or set it inline when running: `GEMINI_API_KEY="your-key" python src/app.py`
  
  **CHROMA_DIR** (Optional):
  - Path to persist the vector store (defaults to `.chroma`)
  - Example: `export CHROMA_DIR="./data/chroma"`
- Run the API:
  - `python src/app.py` (or `uvicorn src.app:app --reload`)

### Frontend (Next.js)
- Install Node dependencies:
  - `cd frontend && npm install`
- Run the UI (defaults to http://localhost:3000):
  - `npm run dev`
- Configure API base (optional):
  - Set `NEXT_PUBLIC_API_BASE` (defaults to `http://localhost:8000`)
- Use the UI to ingest products (name, keywords, image URLs) and search semantically.

### API
- `POST /generate_description`
  - Body: `{ name: string, keywords: [string], image_urls: [string] }`
  - Processes each image individually with Gemini, then collates descriptions into one comprehensive visual description.
  - Returns: `{ description: string }`
- `POST /ingest`
  - Body: `{ name: string, keywords: [string], image_urls: [string], description: string }`
  - Description is required (must be generated via `/generate_description` first).
  - Generates embedding from description and stores vector + metadata in ChromaDB.
  - Returns: `{ product_id: string, description: string, metadata: object }`
- `POST /search`
  - Body: `{ query: string, top_k?: int }` (default top_k: 5)
  - Performs semantic similarity search using query embedding.
  - Returns: `{ results: [{ product_id, score, metadata }] }`

### Notes
- Embeddings use `sentence-transformers/all-MiniLM-L6-v2` via Chroma’s HuggingFace integration (change in `vector_store.py` if desired).
- Gemini calls use image URLs; ensure the URLs are publicly reachable. Replace the `generate_description` logic if you already have descriptions.
- This is a minimal reference implementation; production deployments should add auth, validation hardening, retries, and monitoring.

