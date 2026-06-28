"""
Enterprise Knowledge Assistant

Test Runner

Hour 5 - Vector Database

Pipeline

PDF Loader
    ↓
Chunker
    ↓
Embeddings
    ↓
Vector Indexer
    ↓
Similarity Search
"""

from __future__ import annotations

import sys
from pathlib import Path

from sentence_transformers import SentenceTransformer

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import settings
from app.core.logger import configure_logger

from ingestion.parsers.loader import PDFLoader
from ingestion.chunking.chunker import DocumentChunker
from ingestion.embeddings.embeddings import EmbeddingGenerator
from ingestion.vector_store.indexer import VectorIndexer


def divider(title: str) -> None:
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)


def main() -> None:

    configure_logger()

    # ---------------------------------------------------------
    # Loader
    # ---------------------------------------------------------

    divider("LOADING DOCUMENTS")

    loader = PDFLoader(
        settings.RAW_DATA_PATH
    )

    pages = loader.load_documents()

    loader.print_summary()

    # ---------------------------------------------------------
    # Chunker
    # ---------------------------------------------------------

    divider("CHUNKING DOCUMENTS")

    chunker = DocumentChunker(

        chunk_size=settings.CHUNK_SIZE,

        chunk_overlap=settings.CHUNK_OVERLAP,

    )

    chunks = chunker.chunk_documents(
        pages
    )

    chunker.print_summary()

    # ---------------------------------------------------------
    # Embeddings
    # ---------------------------------------------------------

    divider("GENERATING EMBEDDINGS")

    embedding_generator = (
        EmbeddingGenerator()
    )

    embedded_chunks = (
        embedding_generator.generate_embeddings(
            chunks
        )
    )

    embedding_generator.print_summary()

    # ---------------------------------------------------------
    # Indexer
    # ---------------------------------------------------------

    divider("INDEXING INTO VECTOR DATABASE")

    indexer = VectorIndexer()

    print()

    print(
        f"Collection Exists : "
        f"{indexer.collection_exists()}"
    )

    print()

    if indexer.count() > 0:

        print(
            "Existing vectors detected."
        )

        print(
            "Resetting collection..."
        )

        indexer.reset_collection()

    indexer.index_documents(
        embedded_chunks
    )

    indexer.persist()

    indexer.print_summary()

    # ---------------------------------------------------------
    # Collection Info
    # ---------------------------------------------------------

    divider("COLLECTION INFORMATION")

    print(
        f"Collection : "
        f"{settings.VECTOR_COLLECTION_NAME}"
    )

    print(
        f"Vector Count : "
        f"{indexer.count()}"
    )

    print()

    print("Indexed Documents")

    print("--------------------")

    for document in indexer.list_documents():

        print(document)

    print()

    print("Categories")

    print("--------------------")

    for category in indexer.list_categories():

        print(category)

    # ---------------------------------------------------------
    # Similarity Search
    # ---------------------------------------------------------

    divider("SIMILARITY SEARCH TEST")

    query = (
        "How do I reset my password?"
    )

    print(
        f"Query : {query}"
    )

    model = SentenceTransformer(
        settings.EMBEDDING_MODEL
    )

    query_embedding = model.encode(

        query,

        normalize_embeddings=True,

    ).tolist()

    results = indexer.similarity_search(

        query_embedding=query_embedding,

        top_k=5,

    )

    print()

    print(
        f"Retrieved {len(results)} results"
    )

    print()

    for index, result in enumerate(

        results,

        start=1,

    ):

        print("-" * 80)

        print(
            f"Result #{index}"
        )

        print(
            f"Similarity : {result.score:.4f}"
        )

        print(
            f"Document : "
            f"{result.document}"
        )

        print(
            f"Page : "
            f"{result.page}"
        )

        print(
            f"Category : "
            f"{result.category}"
        )

        print()

        preview = result.text[:300]

        print(preview)

        print()

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    divider("INDEXER STATISTICS")

    statistics = (
        indexer.export_statistics()
    )

    for key, value in statistics.items():

        print(
            f"{key:25}: {value}"
        )

    divider("HOUR 5 COMPLETED SUCCESSFULLY")


if __name__ == "__main__":
    main()
