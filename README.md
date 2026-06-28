````markdown
# Enterprise Knowledge Assistant

An AI-powered Enterprise Knowledge Assistant that enables employees to query internal organizational documents using natural language. The application leverages a Retrieval-Augmented Generation (RAG) pipeline to retrieve relevant information from enterprise knowledge bases and generate grounded responses with source citations.

---

## Project Status

| Stage | Status |
|-------|:------:|
| Project Initialization | ✅ Completed |
| Document Loading Pipeline | ✅ Completed |
| Semantic Chunking Pipeline | ✅ Completed |
| Embedding Generation | ⏳ Upcoming |
| Vector Database | ⏳ Upcoming |
| Semantic Retrieval | ⏳ Upcoming |
| RAG Pipeline | ⏳ Upcoming |
| FastAPI Backend | ⏳ Upcoming |
| Streamlit Frontend | ⏳ Upcoming |
| Deployment | ⏳ Upcoming |

---

# Features

### Completed

- Recursive PDF discovery
- Page-wise text extraction
- Metadata generation
- Production-grade logging
- Semantic recursive chunking
- Stable chunk identifiers
- Chunk statistics
- Corpus analysis
- Modular architecture

### Planned

- OpenAI Embeddings
- ChromaDB Vector Store
- Semantic Search
- Retrieval-Augmented Generation (RAG)
- FastAPI REST API
- Streamlit Web Interface
- Source Citations
- Conversation Memory
- Evaluation Framework
- Docker Deployment

---

# Tech Stack

| Category | Technology |
|----------|------------|
| Language | Python 3.11+ |
| PDF Processing | PyMuPDF |
| Chunking | LangChain RecursiveCharacterTextSplitter |
| Embeddings | OpenAI Embeddings *(Upcoming)* |
| Vector Database | ChromaDB *(Upcoming)* |
| LLM | OpenAI GPT Models *(Upcoming)* |
| Backend | FastAPI *(Upcoming)* |
| Frontend | Streamlit *(Upcoming)* |

---

# Current Project Structure

```text
enterprise-knowledge-assistant/

app/
│
├── core/
│   ├── config.py
│   └── logger.py
│
ingestion/
│
├── parsers/
│   └── loader.py
│
├── chunking/
│   └── chunker.py
│
scripts/
│
├── test_loader.py
└── test_chunker.py

data/
│
├── raw/
├── processed/
└── vectorstore/

logs/

README.md
requirements.txt
````

---

# Architecture (Current)

```text
PDF Documents
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
Semantic Chunking
      │
      ▼
Chunks Ready for Embeddings
```

---

# Document Loading Pipeline

The document ingestion layer is responsible for converting enterprise PDF documents into structured page objects for downstream processing.

## Responsibilities

* Recursive PDF discovery
* Page-wise extraction
* Text cleaning
* Metadata generation
* Statistics generation

## Output Object

Each page is represented as a `DocumentPage`.

```python
DocumentPage(
    document="GDPR Policy.pdf",
    page=5,
    text="...",
    metadata={
        "document": "...",
        "page": 5,
        "category": "compliance",
        "source": "..."
    }
)
```

---

# Chunking Strategy

The project uses LangChain's `RecursiveCharacterTextSplitter` to preserve semantic structure while preparing documents for embedding.

## Configuration

| Parameter     |                          Value |
| ------------- | -----------------------------: |
| Splitter      | RecursiveCharacterTextSplitter |
| Chunk Size    |                 900 Characters |
| Chunk Overlap |                 150 Characters |

---

## Separator Hierarchy

The splitter recursively attempts to preserve semantic boundaries using the following priority:

1. Paragraphs
2. Bullet Lists
3. New Lines
4. Sentences
5. Words
6. Character Fallback

This minimizes splitting inside policy sections, API documentation, FAQ entries, and procedural instructions.

---

## Corpus Analysis

The selected configuration is based on analysis of the enterprise knowledge base.

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

Using a chunk size of **900 characters** preserves most pages as complete semantic units while still allowing larger pages to be recursively divided when necessary.

This provides:

* Better semantic cohesion
* Lower embedding redundancy
* Improved retrieval precision
* Fewer fragmented chunks

---

## Why 150 Character Overlap?

A 150-character overlap preserves context across chunk boundaries while avoiding excessive duplication.

Benefits include:

* Better retrieval for boundary-spanning queries
* Reduced semantic loss
* Improved answer grounding

---

## Metadata Propagation

Every generated chunk inherits page metadata and adds chunk-specific metadata.

Example:

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

# Current Processing Pipeline

```text
Enterprise PDFs
        │
        ▼
PDF Discovery
        │
        ▼
Page Extraction
        │
        ▼
Text Cleaning
        │
        ▼
Metadata Generation
        │
        ▼
Recursive Semantic Chunking
        │
        ▼
Document Chunks
```

---

# Current Progress

| Module               | Status |
| -------------------- | :----: |
| Logging              |    ✅   |
| Configuration        |    ✅   |
| PDF Loader           |    ✅   |
| Metadata Generation  |    ✅   |
| Statistics           |    ✅   |
| Chunking Pipeline    |    ✅   |
| Chunk Metadata       |    ✅   |
| Chunk Statistics     |    ✅   |
| Embedding Generation |    ⏳   |
| Vector Store         |    ⏳   |
| Retriever            |    ⏳   |
| RAG                  |    ⏳   |
| API                  |    ⏳   |
| Frontend             |    ⏳   |

---

# Upcoming Milestones

* Generate OpenAI embeddings
* Build ChromaDB vector store
* Implement semantic retrieval
* Develop Retrieval-Augmented Generation pipeline
* Build FastAPI backend
* Develop Streamlit user interface
* Add evaluation framework
* Deploy application

---
