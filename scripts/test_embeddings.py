"""
Test runner for the embedding generation pipeline.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import settings
from app.core.logger import configure_logger
from ingestion.chunking.chunker import DocumentChunker
from ingestion.embeddings.embeddings import EmbeddingGenerator
from ingestion.parsers.loader import PDFLoader


def main() -> None:

    configure_logger()

    print("=" * 80)
    print("LOADING DOCUMENTS")
    print("=" * 80)

    loader = PDFLoader(settings.RAW_DATA_PATH)

    pages = loader.load_documents()

    loader.print_summary()

    print()

    print("=" * 80)
    print("CHUNKING DOCUMENTS")
    print("=" * 80)

    chunker = DocumentChunker(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
    )

    chunks = chunker.chunk_documents(pages)

    chunker.print_summary()

    print()

    print("=" * 80)
    print("GENERATING EMBEDDINGS")
    print("=" * 80)

    generator = EmbeddingGenerator()

    embedded_chunks = generator.generate_embeddings(
        chunks
    )

    generator.print_summary()

    print()

    print("=" * 80)
    print("FIRST EMBEDDING")
    print("=" * 80)

    if embedded_chunks:
        generator.preview_embedding(
            embedded_chunks[0]
        )

    print()

    print("=" * 80)
    print("EMBEDDING STATISTICS")
    print("=" * 80)

    stats = generator.get_statistics()

    for key, value in stats.items():
        print(f"{key:22}: {value}")

    print()

    print("=" * 80)
    print(
        f"TOTAL EMBEDDINGS GENERATED : "
        f"{len(embedded_chunks)}"
    )
    print("=" * 80)


if __name__ == "__main__":
    main()
