# Enterprise Knowledge Assistant

Enterprise Knowledge Assistant is a production-style Retrieval-Augmented Generation (RAG) application for querying internal enterprise documents with natural language. The system ingests PDFs, chunks them semantically, generates local BGE embeddings, stores them in ChromaDB, and serves grounded answers through FastAPI and Streamlit with source citations and conversation memory.

## Project Status

The implementation is complete through the core ingestion → retrieval → generation → UI workflow, including conversation memory. Evaluation and deployment are scaffolded but not yet finished.

| Module                   | Status                    |
| ------------------------ | ------------------------- |
| Project Initialization   | ✅ Completed              |
| Configuration Management | ✅ Completed              |
| Logging                  | ✅ Completed              |
| PDF Loader               | ✅ Completed              |
| Semantic Chunking        | ✅ Completed              |
| Local Embeddings         | ✅ Completed              |
| Vector Store             | ✅ Completed              |
| Hybrid Search            | ✅ Completed              |
| Retriever                | ✅ Completed              |
| Prompt Engineering       | ✅ Completed              |
| RAG Pipeline             | ✅ Completed              |
| FastAPI Backend          | ✅ Completed              |
| Streamlit Frontend       | ✅ Completed              |
| Conversation Memory      | ✅ Completed              |
| Evaluation Framework     | ✅ Completed              |
| Unit Testing             | ✅ Completed              |
| Docker Support           | ✅ Completed              |
| Cloud Deployment         | Optional / Not Deployed   |

> Note: The application currently runs locally using FastAPI and Streamlit. Docker configuration is included for portable deployment. Public cloud deployment has not been performed because it was an optional project requirement.

## Tech Stack

| Category        | Technology                     |
| ---------------- | ------------------------------ |
| Language         | Python 3.12                    |
| PDF Processing   | PyMuPDF                        |
| Chunking         | RecursiveCharacterTextSplitter |
| Embeddings       | BAAI/bge-base-en-v1.5 (local)  |
| Vector Database  | ChromaDB                       |
| Retrieval        | Hybrid Search (BM25 + Vector)  |
| Re-ranking       | MMR                            |
| LLM              | Groq (Llama 3.3 70B Versatile) |
| Backend          | FastAPI                        |
| Frontend         | Streamlit                      |
| Validation       | Pydantic v2                    |

The project uses LangChain selectively for semantic chunking and conversation memory while implementing the retrieval, indexing, and RAG orchestration as custom modules. Local BGE embeddings are generated using sentence-transformers, and inference is performed using the Groq API.

## Architecture

![Architecture diagram](docs/architecture.svg)

The text version below is the same pipeline for environments that don't render SVG (e.g. plain-text README viewers):

```text
Enterprise PDFs
        │
        ▼
PDF Loader
        │
        ▼
Semantic Chunking
        │
        ▼
Local BGE Embeddings
        │
        ▼
ChromaDB
        │
        ▼
Hybrid Search (BM25 + Vector Search)
        │
        ▼
MMR Re-ranking
        │
        ▼
Conversation Memory
        │
        ▼
Prompt Builder
        │
        ▼
Groq LLM
        │
        ▼
FastAPI
        │
        ▼
Streamlit UI
```

## Project Structure

```text
Enterprise-Knowledge-Assistant/
├── app/
│   ├── api/
│   ├── core/
│   └── schemas/
├── ingestion/
│   ├── chunking/
│   ├── embeddings/
│   ├── parsers/
│   └── vector_store/
├── retrieval/
├── services/
├── scripts/
├── evaluation/
├── tests/
├── data/
│   ├── raw/
│   ├── processed/
│   └── vectorstore/
├── logs/
├── .streamlit/
├── Dockerfile
├── docker-compose.yml
├── start.sh
├── requirements.txt
├── pyproject.toml
├── setup.cfg
├── .env.example
└── app.py
```

## Conversation Memory

The application includes a session-based conversation memory layer for follow-up questions and contextual dialogue.

### What it provides

- Session-based memory with isolated conversation histories
- A `ConversationManager` for organizing sessions
- A `ConversationMemory` object per session
- Previous conversation history injected into the prompt
- Follow-up question support, e.g. "What about contractors?" or "Summarize that."
- Configurable history limit via `MEMORY_MAX_HISTORY`
- Automatic trimming of old turns
- Clear chat / session reset support

### Memory Flow

```text
User Question
        │
        ▼
Conversation Memory
        │
        ▼
Prompt Builder
        │
        ▼
Groq LLM
```

## FastAPI Backend

The backend exposes a REST API for querying the knowledge base and retrieving grounded answers.

### Endpoints

| Method | Endpoint  | Description                                       |
| ------ | --------- | -------------------------------------------------- |
| GET    | `/`       | API information                                    |
| GET    | `/health` | Health check                                       |
| POST   | `/ask`    | Ask a question against the indexed knowledge base  |
| GET    | `/docs`   | Swagger UI                                         |
| GET    | `/redoc`  | ReDoc documentation                                |

### Example Request

```json
{
  "question": "What is the password policy?",
  "session_id": "optional-session-id"
}
```

### Example Response

```json
{
  "answer": "The password policy requires strong passwords and MFA for privileged accounts.",
  "sources": [
    {
      "document": "Password Policy.pdf",
      "page": 12,
      "category": "compliance",
      "chunk_id": "password_policy_p012_c001"
    }
  ],
  "confidence": 0.94,
  "latency": 1.62,
  "retrieved_documents": 5
}
```

## Streamlit Frontend

The Streamlit app (`app.py`) provides a chat-style experience for non-technical users.

### Included UI Features

- Sidebar dashboard with live config and retrieval settings
- Question input box
- Source citations in the answer view (document, page, category, chunk ID)
- Confidence score display
- Latency display
- Expandable source documents
- Clear Chat support
- Backend health check (sidebar status indicator)
- Session persistence for follow-up questions

## RAG Pipeline

The application follows a grounded retrieval-and-generation flow.

```text
Question
        │
        ▼
Conversation Memory
        │
        ▼
Hybrid Search (BM25 + Vector Search)
        │
        ▼
MMR Re-ranking
        │
        ▼
Prompt Builder
        │
        ▼
Groq LLM
        │
        ▼
Grounded Answer
        │
        ▼
Source Citations
```

## Features

### Completed

- Recursive PDF loading
- Semantic chunking
- Local embeddings with BGE
- Persistent ChromaDB storage
- Batch indexing
- Hybrid Search (BM25 + Dense Retrieval)
- MMR re-ranking
- Prompt engineering with hallucination guardrails
- Source citations (document, page, category, chunk ID)
- FastAPI REST API
- Swagger UI / ReDoc
- Streamlit frontend
- Conversation memory
- Session management
- Production logging
- Evaluation framework (benchmark question set + metrics)
- Unit testing (pytest)
- Docker configuration

### In Progress / Planned

- CI/CD pipeline
- Authentication
- Cloud deployment (backend + frontend)

## Performance Metrics

| Metric              | Value                    |
| ------------------- | ------------------------- |
| Documents           | 22                        |
| Pages               | 445                       |
| Characters          | 390,366                   |
| Indexed Chunks      | ≈800 (depends on corpus)  |
| Embedding Dimension | 768                       |
| Retrieval Strategy  | Hybrid Search + MMR       |
| Top K               | 5                         |

These figures reflect the current local document set and will change as the knowledge base grows.

## Design Principles

The project is structured around enterprise-grade software engineering principles:

- Separation of Concerns
- Single Responsibility Principle
- Modular Architecture
- Configuration-driven Design
- Immutable Data Models
- Type Safety
- Production Logging
- Enterprise RAG Architecture

## Installation

1. **Clone the repository**

```bash
git clone https://github.com/Surya-Teja-Kancharla/Enterprise-Knowledge-Assistant.git
cd Enterprise-Knowledge-Assistant
```

2. **Create and activate a virtual environment**

```bash
python -m venv venv
source venv/bin/activate
```

On Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

```bash
cp .env.example .env
```

Then update the values for your Groq API key and model configuration.

5. **Run the embedding and indexing pipeline**

```bash
python scripts/test_embeddings.py
python scripts/test_indexer.py
python scripts/test_retrieval.py
python scripts/test_rag.py
```

6. **Start the FastAPI backend**

```bash
uvicorn app.api.main:app --host 0.0.0.0 --port 8000
```

7. **Start the Streamlit frontend**

```bash
streamlit run app.py
```

The frontend expects the backend at `http://127.0.0.1:8000` by default — make sure step 6 is running first.

## Configuration

The application uses environment variables defined in `.env`.

| Variable          | Description                  |
| ------------------ | ----------------------------- |
| `GROQ_API_KEY`     | API key for Groq access       |
| `GROQ_MODEL`       | Groq model name                |
| `EMBEDDING_MODEL`  | Local embedding model          |
| `VECTOR_DB_PATH`   | ChromaDB storage path          |
| `CHUNK_SIZE`       | Semantic chunk size             |
| `CHUNK_OVERLAP`    | Chunk overlap size              |
| `TOP_K`            | Number of retrieved chunks      |

See `app/core/config.py` for the full settings schema, including API host/port, logging level, and memory configuration.

## Running with Docker (Unverified)

A `Dockerfile` and `docker-compose.yml` are included in the repo, but this path has not yet been tested end-to-end. If you try it:

```bash
docker compose up --build
```

If this doesn't work out of the box, fall back to the manual installation steps above and treat the Docker files as a starting point rather than a finished setup.

## Technical Decisions

This section explains the *why*, not just the *what*, behind the stack choices above.

**Embeddings: local BGE (`BAAI/bge-base-en-v1.5`) instead of an API-based embedding model.**
Running embeddings locally avoids per-document API cost and external rate limits during ingestion, and keeps the entire pipeline runnable offline once the model is cached. The trade-off is one-time model download size and CPU/GPU load during indexing — acceptable for a 22-document, 671-chunk corpus, but a fair question to raise in review is whether this still holds at 10,000+ documents.

**Vector store: ChromaDB instead of FAISS or a managed service (Pinecone/Weaviate).**
ChromaDB gives persistent on-disk storage, a simple Python API, and metadata filtering (document, page, category) without standing up external infrastructure. FAISS would need a separate metadata store bolted on; Pinecone/Weaviate add network dependency and cost for a single-node deployment that doesn't need them yet.

**Chunking: `RecursiveCharacterTextSplitter`, chunk size 900 / overlap 150.**
Recursive splitting respects paragraph and sentence boundaries before falling back to hard character cuts, which keeps individual chunks semantically coherent for retrieval. A chunk size of 900 characters balances two failure modes: too small and chunks lose surrounding context needed to answer a question; too large and irrelevant text dilutes the embedding, hurting retrieval precision. The 150-character overlap reduces the chance that an answer-bearing sentence gets split exactly at a chunk boundary.

**Hybrid Search: BM25 + Dense Vector Retrieval.**
Hybrid search combines dense vector retrieval with BM25 keyword search to improve recall. Vector search captures semantic similarity, while BM25 retrieves exact keyword matches such as policy names, document IDs, and acronyms. The merged results are diversified using MMR before being passed to the language model.

**Re-ranking: MMR (Maximal Marginal Relevance) instead of plain top-k similarity, Top K = 5.**
Plain similarity search on enterprise documents tends to return several near-duplicate chunks from the same paragraph or repeated boilerplate (e.g., headers repeated across pages of the same policy doc). MMR explicitly penalizes redundancy between selected chunks, so the 5 chunks passed to the LLM are more likely to cover distinct facts rather than restating the same sentence five times.

**LLM: Groq (Llama 3.3 70B Versatile) instead of OpenAI/Anthropic APIs.**
Groq's inference is fast enough to keep end-to-end query latency low, which matters for a chat-style UI where users expect near-real-time responses. Llama 3.3 70B is capable enough for grounded extractive QA over retrieved context, which is a narrower task than open-ended generation. The trade-off against GPT-4-class models is somewhat weaker reasoning on ambiguous or multi-hop questions — acceptable here since the assignment's QA examples are direct lookups, not multi-step reasoning.

**Selective LangChain usage.**
The project uses LangChain selectively for semantic chunking (`RecursiveCharacterTextSplitter`) and conversation memory (`ConversationBufferMemory`) while implementing the retrieval, indexing, and RAG orchestration as custom modules. This approach balances the convenience of mature components with the transparency and control of custom implementation.

**Hallucination prevention: prompt-level grounding constraint.**
The system prompt instructs the model to answer only from retrieved context and to state explicitly when the answer isn't in the knowledge base, rather than relying solely on retrieval quality to prevent fabrication. This is a necessary but not sufficient safeguard — it doesn't catch cases where the LLM ignores the instruction, which is why an evaluation framework (below) is needed to actually measure how often this happens rather than assuming the prompt works.

## Known Limitations

- **Evaluation framework scaffolded but not yet run.** The benchmark infrastructure (`evaluation/benchmark.py`, `evaluation/report.py`, `scripts/test_benchmark.py`) exists with retrieval precision, document accuracy, page accuracy, groundedness, and keyword accuracy metrics, but no benchmark results have been generated yet.
- **Not deployed.** The application runs only on localhost; there is no public URL for the API or the UI.
- **No authentication.** Anyone with network access to the running API can query it; this is acceptable for local development but not production-ready.
- **No re-ranking model beyond MMR.** Retrieved chunks are re-ranked using MMR for diversity but not scored with a cross-encoder for relevance.
- **No query rewriting.** Ambiguous or multi-part questions are handled only as well as a single retrieval pass allows.
- **Docker infrastructure exists but untested.** `Dockerfile`, `docker-compose.yml`, and `start.sh` are present, but `docker compose up` has not been run end-to-end against this codebase. Treat it as a starting point, not a tested deployment path.
- **Single-node, no scalability testing.** ChromaDB here runs as an embedded, single-process store. At higher document volumes or concurrent users, this would need to move to a client-server ChromaDB deployment or a managed vector DB, and ingestion would need a queue rather than synchronous batch processing.

## Future Improvements

- ✅ Build the evaluation framework: benchmark question set with expected answers/sources, scored for retrieval precision, document accuracy, page accuracy, groundedness, and keyword accuracy (infrastructure complete, awaiting execution)
- Run the Docker build end-to-end and add a CI step that validates it.
- Add authentication to the FastAPI backend before any public deployment.
- Deploy backend and frontend, and publish the resulting URLs here.
- Add structured logging and metrics for latency and retrieval quality in production, not just local logs.
- Implement query rewriting for ambiguous or multi-part questions.
- Add cross-encoder re-ranking for improved relevance scoring.
- Implement user feedback collection for continuous improvement.
- Set up CI/CD pipeline for automated testing and deployment.

## Demo

[Watch the demo on YouTube](https://youtu.be/a-cdU2CvcLM)

## System Design Document

[View the system design document](assets/System Design Document.pdf)

## High Level Architecture

[View the system design document](assets\enterprise_knowledge_assistant_architecture.png)
