# Enterprise Knowledge Assistant

Enterprise Knowledge Assistant is a production-style Retrieval-Augmented Generation (RAG) application for querying internal enterprise documents with natural language. The system ingests PDFs, chunk them semantically, creates local BGE embeddings, stores them in ChromaDB, and serves grounded answers through FastAPI and Streamlit with source citations and conversation memory.

## Project Status

The implementation is now complete through the core Hour 11 workflow, including the ingestion pipeline, retrieval layer, backend API, frontend UI, and conversation memory.

| Module                   | Status       |
| ------------------------ | ------------ |
| Project Initialization   | ✅ Completed |
| Configuration Management | ✅ Completed |
| Logging                  | ✅ Completed |
| PDF Loader               | ✅ Completed |
| Semantic Chunking        | ✅ Completed |
| Local Embeddings         | ✅ Completed |
| Vector Store             | ✅ Completed |
| Retriever                | ✅ Completed |
| Prompt Engineering       | ✅ Completed |
| RAG Pipeline             | ✅ Completed |
| FastAPI Backend          | ✅ Completed |
| Streamlit Frontend       | ✅ Completed |
| Conversation Memory      | ✅ Completed |
| Evaluation Framework     | ⏳ Pending   |
| Deployment               | ⏳ Pending   |

## Tech Stack

| Category        | Technology                     |
| --------------- | ------------------------------ |
| Language        | Python 3.12                    |
| PDF Processing  | PyMuPDF                        |
| Chunking        | RecursiveCharacterTextSplitter |
| Embeddings      | BAAI/bge-base-en-v1.5          |
| Vector Database | ChromaDB                       |
| Retrieval       | MMR Search                     |
| LLM             | Groq (Llama 3.3 70B Versatile) |
| Backend         | FastAPI                        |
| Frontend        | Streamlit                      |
| Validation      | Pydantic v2                    |

## Architecture

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
MMR Retriever
        │
        ▼
Conversation Memory
        │
        ▼
Prompt Engineering
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
Enterprise Knowledge Assistant/
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
├── memory/
├── scripts/
├── data/
│   ├── raw/
│   ├── processed/
│   └── vectorstore/
├── logs/
└── README.md
```

## Conversation Memory

The application includes a session-based conversation memory layer for follow-up questions and contextual dialogue.

### What it provides

- Session-based memory with isolated conversation histories
- A ConversationManager for organizing sessions
- A ConversationMemory object for each session
- Previous conversation history injected into the prompt
- Follow-up question support such as “What about contractors?” or “Summarize that.”
- Configurable history limit via MEMORY_MAX_HISTORY
- Automatic trimming of old turns
- Clear chat/session reset support

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

| Method | Endpoint | Description                                       |
| ------ | -------- | ------------------------------------------------- |
| GET    | /        | API information                                   |
| GET    | /health  | Health check                                      |
| POST   | /ask     | Ask a question against the indexed knowledge base |
| GET    | /docs    | Swagger UI                                        |
| GET    | /redoc   | ReDoc documentation                               |

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

The Streamlit app provides a modern chat-style experience for non-technical users.

### Included UI Features

- Modern sidebar dashboard
- Question input box
- Source citations in the answer view
- Confidence score display
- Latency display
- Expandable source documents
- Clear Chat support
- Session persistence for follow-up questions

## RAG Pipeline

The application follows a grounded retrieval-and-generation flow.

```text
Question
        │
        ▼
Retriever
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
- MMR retrieval
- Prompt engineering
- Hallucination prevention
- Source citations
- FastAPI REST API
- Swagger UI
- Streamlit frontend
- Conversation memory
- Session management
- Production logging

### Planned

- Evaluation framework
- Authentication
- Docker deployment
- CI/CD pipeline

## Performance Metrics

| Metric              | Value   |
| ------------------- | ------- |
| Documents           | 22      |
| Pages               | 445     |
| Characters          | 390,366 |
| Indexed Chunks      | 671     |
| Embedding Dimension | 768     |
| Retrieval           | MMR     |
| Top K               | 5       |

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

1. Clone the repository

```bash
git clone https://github.com/your-username/enterprise-knowledge-assistant.git
cd enterprise-knowledge-assistant
```

2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

On Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Configure environment variables

```bash
cp .env.example .env
```

Then update the values for your Groq and model configuration.

5. Run the embedding and indexing pipeline

```bash
python scripts/test_embeddings.py
python scripts/test_indexer.py
```

6. Start the FastAPI backend

```bash
uvicorn app.api.main:app --host 0.0.0.0 --port 8000
```

7. Start the Streamlit frontend

```bash
streamlit run app.py
```

## Configuration

The application uses environment variables defined in .env.

| Variable        | Description                |
| --------------- | -------------------------- |
| GROQ_API_KEY    | API key for Groq access    |
| GROQ_MODEL      | Groq model name            |
| EMBEDDING_MODEL | Local embedding model      |
| VECTOR_DB_PATH  | ChromaDB storage path      |
| CHUNK_SIZE      | Semantic chunk size        |
| CHUNK_OVERLAP   | Chunk overlap size         |
| TOP_K           | Number of retrieved chunks |

## API Example

### Request

```json
{
  "question": "What is the password policy?",
  "session_id": "optional-session-id"
}
```

### Response

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

## Future Roadmap

- Evaluation framework and benchmark suite
- Authentication and authorization
- Docker-based deployment
- CI/CD automation
- Monitoring and observability
- Cloud deployment readiness
