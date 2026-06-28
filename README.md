````markdown
# Enterprise Knowledge Assistant

An AI-powered Enterprise Knowledge Assistant that enables employees to query internal organizational documents using natural language.

## 1. Project Status

| Stage                         |    Status    |
| ----------------------------- | :----------: |
| Project Initialization        | ✅ Completed |
| Document Loading Pipeline     | ✅ Completed |
| Semantic Chunking Pipeline    | ✅ Completed |
| Embedding Generation Pipeline | ✅ Completed |
| Vector Database               | ✅ Completed |
| Semantic Retrieval            | ✅ Completed |
| Prompt Engineering            | ✅ Completed |
| RAG Pipeline                  | ✅ Completed |
| FastAPI Backend               | ✅ Completed |
| Streamlit Frontend            | ⏳ Upcoming  |
| Deployment                    | ⏳ Upcoming  |

## 2. Features

### Completed

- Recursive PDF discovery
- Page-wise text extraction
- Metadata generation
- Production-grade logging
- Semantic recursive chunking
- Stable chunk identifiers
- Local BGE embedding generation
- Batch embedding pipeline
- Embedding validation
- Embedding statistics
- Corpus analysis
- Persistent ChromaDB vector store
- Incremental vector indexing
- Batch upsert operations
- Semantic similarity search
- MMR retrieval
- Metadata filtering
- Prompt engineering
- Hallucination prevention
- Source citations
- Complete Retrieval-Augmented Generation (RAG) pipeline
- FastAPI REST API
- OpenAPI (Swagger) Documentation
- Health Check Endpoint
- Request Validation
- Structured API Responses
- Global Exception Handling
- Request Logging Middleware
- Response Latency Tracking

### Planned

- Streamlit Web Interface
- Conversation Memory
- Evaluation Framework
- Docker Deployment

## 3. Tech Stack

| Category        | Technology                     |
| --------------- | ------------------------------ |
| Language        | Python 3.11+                   |
| PDF Processing  | PyMuPDF                        |
| Chunking        | RecursiveCharacterTextSplitter |
| Embeddings      | BAAI/bge-base-en-v1.5          |
| Vector Database | ChromaDB                       |
| Retrieval       | MMR Similarity Search          |
| LLM             | Groq Llama 3.3-70B Versatile   |
| Backend         | FastAPI                        |
| API Validation  | Pydantic v2                    |
| ASGI Server     | Uvicorn                        |
| Frontend        | Streamlit _(Upcoming)_         |

## 4. Current Project Structure

```text
Enterprise Knowledge Assistant/
├── app/
│   ├── api/
│   │   ├── main.py
│   │   └── routes.py
│   ├── schemas/
│   │   └── api.py
│   ├── core/
│   │   ├── config.py
│   │   └── logger.py
│   ├── utils/
├── ingestion/
│   ├── parsers/
│   ├── chunking/
│   ├── embeddings/
│   └── vector_store/
├── retrieval/
│   ├── retrieval.py
│   ├── models.py
│   └── filters.py
├── services/
│   ├── prompts.py
│   └── rag.py
├── scripts/
│   ├── test_loader.py
│   ├── test_chunker.py
│   ├── test_embeddings.py
│   ├── test_indexer.py
│   ├── test_retrieval.py
│   ├── test_rag.py
│   └── test_api.py
├── data/
├── vectorstore/
└── logs/
```

## 5. Current Architecture

```text
Enterprise PDFs
        │
        ▼
PDF Loader
        │
        ▼
Recursive Chunking
        │
        ▼
Local BGE Embeddings
        │
        ▼
ChromaDB
        │
        ▼
MMR Retrieval
        │
        ▼
Prompt Engineering
        │
        ▼
Groq LLM
        │
        ▼
FastAPI REST API
        │
        ▼
JSON Response
```

## 6. FastAPI Backend

The Enterprise Knowledge Assistant exposes a REST API built with FastAPI.

### Endpoints

| Method | Endpoint  | Description                         |
| ------ | --------- | ----------------------------------- |
| GET    | `/`       | API information                     |
| GET    | `/health` | Health status                       |
| POST   | `/ask`    | Query the enterprise knowledge base |
| GET    | `/docs`   | Interactive Swagger documentation   |
| GET    | `/redoc`  | ReDoc documentation                 |

---

### Request

```json
{
  "question": "What is the password policy?"
}
```

---

### Response

```json
{
  "answer": "...",
  "sources": [
    {
      "document": "Password Policy.pdf",
      "page": 12,
      "category": "compliance",
      "chunk_id": "..."
    }
  ],
  "confidence": 0.94,
  "latency": 1.62,
  "retrieved_documents": 5
}
```

---

### Features

- Automatic OpenAPI generation
- Swagger UI
- Pydantic validation
- Request logging
- Exception handling
- Response models
- Health monitoring

## 7. Prompt Engineering

The language model receives a constrained system prompt to ensure grounded responses.

Rules enforced:

- Answer only using retrieved context.
- Never fabricate information.
- Always provide source citations.
- If no supporting context exists, respond exactly:

```text
I could not find this information in the provided knowledge base.
```

This approach minimizes hallucinations and ensures enterprise-safe responses.

## 8. Retrieval-Augmented Generation (RAG) Pipeline

The application combines semantic retrieval with large language model generation.

```text
User Question
        │
        ▼
MMR Retriever
        │
        ▼
Top 5 Relevant Chunks
        │
        ▼
Prompt Builder
        │
        ▼
Groq Llama 3.3
        │
        ▼
Grounded Answer
        │
        ▼
Source Citations
```

Each response includes:

- Grounded answer
- Source document citations
- Retrieved document count
- End-to-end latency

## 9. Current Processing Pipeline

```text
Enterprise PDFs
        │
        ▼
PDF Loader
        │
        ▼
Recursive Chunking
        │
        ▼
Local BGE Embeddings
        │
        ▼
ChromaDB
        │
        ▼
MMR Retrieval
        │
        ▼
Prompt Engineering
        │
        ▼
Groq LLM
        │
        ▼
FastAPI REST API
        │
        ▼
JSON Response
```

## 10. Current Progress

| Module                | Status |
| --------------------- | :----: |
| Logging               |   ✅   |
| Configuration         |   ✅   |
| PDF Loader            |   ✅   |
| Chunking Pipeline     |   ✅   |
| Local Embeddings      |   ✅   |
| ChromaDB Vector Store |   ✅   |
| Vector Indexing       |   ✅   |
| Semantic Retrieval    |   ✅   |
| MMR Search            |   ✅   |
| Prompt Engineering    |   ✅   |
| RAG Pipeline          |   ✅   |
| Source Citations      |   ✅   |
| FastAPI Backend       |   ✅   |
| Swagger Documentation |   ✅   |
| Health Monitoring     |   ✅   |
| Streamlit UI          |   ⏳   |

## 11. Next Milestones

- Build Streamlit user interface
- Add conversation memory
- Implement authentication
- Add evaluation framework
- Dockerize the application
- Deploy the complete system

## 12. Pipeline Performance

| Metric               |                 Value |
| -------------------- | --------------------: |
| Documents            |               22 PDFs |
| Pages                |                   445 |
| Chunks Indexed       |                   671 |
| Embedding Model      | BAAI/bge-base-en-v1.5 |
| Vector Database      |              ChromaDB |
| Retrieval            |                   MMR |
| Top K                |                     5 |
| API Framework        |               FastAPI |
| Test Queries         |                    10 |
| Successful Responses |                    10 |

Each response is generated through the complete Retrieval-Augmented Generation (RAG) pipeline and returned as a structured JSON response with supporting source citations.
| Vector Database | ChromaDB |
| Test Queries | 10 |
| Successful Responses | 10 |
| Average Pipeline Latency | ~11 seconds |

Each response includes grounded answers and source citations generated from the retrieved enterprise documents.
│
├── raw/
├── processed/
└── vectorstore/

logs/

README.md
requirements.txt

````

---

# Current Architecture

```text
Enterprise PDFs
        │
        ▼
PDF Loader
        │
        ▼
DocumentPage
        │
        ▼
Recursive Semantic Chunker
        │
        ▼
DocumentChunk
        │
        ▼
OpenAI Embedding Generator
        │
        ▼
EmbeddedChunk
        │
        ▼
Ready for ChromaDB
````

---

# Document Loading Pipeline

The document ingestion layer converts enterprise PDF documents into structured page objects.

## Responsibilities

- Recursive PDF discovery
- Page-wise text extraction
- Text normalization
- Metadata generation
- Corpus statistics

## Output Object

```python
DocumentPage(
    document="GDPR Policy.pdf",
    page=5,
    text="...",
    metadata={
        "document":"...",
        "page":5,
        "category":"compliance",
        "source":"..."
    }
)
```

---

# Chunking Strategy

The project uses LangChain's `RecursiveCharacterTextSplitter` to preserve semantic boundaries before embedding generation.

## Configuration

| Parameter     |                          Value |
| ------------- | -----------------------------: |
| Splitter      | RecursiveCharacterTextSplitter |
| Chunk Size    |                 900 Characters |
| Chunk Overlap |                 150 Characters |

## Separator Priority

1. Paragraphs
2. Bullet Lists
3. New Lines
4. Sentences
5. Words
6. Character Fallback

This hierarchy minimizes fragmentation of policy sections, API endpoints, procedural guides, and FAQ entries.

---

# Corpus Analysis

The chunking strategy is based on analysis of the enterprise corpus.

| Metric              |                         Value |
| ------------------- | ----------------------------: |
| Documents           |                            22 |
| Pages               |                           445 |
| Characters          |                       390,366 |
| Average Page Length |                877 Characters |
| Largest Document    | NovaCRM User Guide (31 Pages) |

---

## Why 900 Character Chunks?

The average extracted page length is approximately **877 characters**.

Using a chunk size of **900 characters** preserves most pages as complete semantic units while allowing larger pages to be recursively divided.

Benefits include:

- Higher semantic cohesion
- Lower embedding redundancy
- Improved retrieval precision
- Reduced chunk fragmentation

---

## Why 150 Character Overlap?

A 150-character overlap preserves contextual continuity between adjacent chunks while avoiding excessive duplication.

Benefits:

- Better retrieval across chunk boundaries
- Reduced semantic loss
- Improved answer grounding

---

# Metadata Propagation

Each generated chunk preserves source information and adds chunk-specific metadata.

```json
{
  "document": "GDPR Policy.pdf",
  "page": 5,
  "category": "compliance",
  "source": "data/raw/compliance/GDPR Policy.pdf",
  "chunk_number": 1,
  "chunk_size": 900,
  "chunk_overlap": 150,
  "chunk_id": "gdpr_policy_p005_c001_a73b4d9e"
}
```

---

# Embedding Pipeline

The embedding pipeline converts semantic document chunks into dense vector representations using a local BGE embedding model.

## Embedding Model

| Parameter  |                         Value |
| ---------- | ----------------------------: |
| Provider   | Local (sentence-transformers) |
| Model      |         BAAI/bge-base-en-v1.5 |
| Dimension  |                           768 |
| Batch Size |                            32 |

---

## Why BAAI/bge-base-en-v1.5?

The BGE (BAAI General Embedding) model is a production-grade open-source embedding model that offers:

- **Free to use locally** - No API costs or rate limits
- **High-quality semantic search** - State-of-the-art performance on retrieval benchmarks
- **Efficient inference** - Runs comfortably on typical development hardware
- **768-dimensional vectors** - Compact yet expressive representations
- **Widely adopted** - Proven in production RAG systems

For a corpus of 22 PDFs (~805 chunks), this model provides excellent retrieval quality without embedding costs.

---

## Embedding Features

- Local inference (no API dependencies)
- Batch processing
- Normalized embeddings
- Embedding dimension validation
- Metadata preservation
- Statistics collection
- Production logging

---

## Embedded Object

```python
EmbeddedChunk(
    chunk_id="gdpr_policy_p005_c001_a73b4d9e",

    text="...",

    embedding=[0.021, -0.084, ...],

    metadata={
        ...
    }
)
```

---

# Current Processing Pipeline

```text
Enterprise PDFs
        │
        ▼
PDF Loader
        │
        ▼
Page Extraction
        │
        ▼
Metadata Generation
        │
        ▼
Recursive Semantic Chunking
        │
        ▼
Document Chunks
        │
        ▼
OpenAI Embeddings
        │
        ▼
Embedded Chunks
```

---

# Current Progress

| Module               | Status |
| -------------------- | :----: |
| Logging              |   ✅   |
| Configuration        |   ✅   |
| PDF Loader           |   ✅   |
| Metadata Generation  |   ✅   |
| Corpus Statistics    |   ✅   |
| Chunking Pipeline    |   ✅   |
| Chunk Metadata       |   ✅   |
| Chunk Statistics     |   ✅   |
| OpenAI Embeddings    |   ✅   |
| Batch Processing     |   ✅   |
| Embedding Validation |   ✅   |
| Vector Store         |   ⏳   |
| Retriever            |   ⏳   |
| RAG Pipeline         |   ⏳   |
| FastAPI              |   ⏳   |
| Streamlit UI         |   ⏳   |

---

# Next Milestones

- Build ChromaDB vector index
- Implement semantic retrieval
- Add metadata filtering
- Implement Retrieval-Augmented Generation (RAG)
- Build FastAPI backend
- Develop Streamlit interface
- Add evaluation framework
- Deploy using Docker

---

# Design Principles

The project follows several software engineering principles:

- Separation of Concerns (SoC)
- Single Responsibility Principle (SRP)
- Immutable Data Models
- Configuration-driven Architecture
- Modular Pipeline Design
- Type-safe Data Flow
- Production-grade Logging
- Enterprise-ready RAG Architecture

---
````
