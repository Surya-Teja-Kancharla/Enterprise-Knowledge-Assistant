"""
Test runner for the document chunking pipeline.
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
    print("GENERATING CHUNKS")
    print("=" * 80)

    chunker = DocumentChunker(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
    )

    chunks = chunker.chunk_documents(pages)

    chunker.print_summary()

    print()

    print("=" * 80)
    print("FIRST FIVE CHUNKS")
    print("=" * 80)

    for chunk in chunks[:5]:
        chunker.preview_chunk(chunk)

    print()

    print("=" * 80)
    print("LAST CHUNK")
    print("=" * 80)

    if chunks:
        chunker.preview_chunk(chunks[-1])

    print()

    print("=" * 80)
    print("FINAL STATISTICS")
    print("=" * 80)

    stats = chunker.get_statistics()

    for key, value in stats.items():
        print(f"{key:20}: {value}")

    print()

    print("=" * 80)
    print(f"TOTAL CHUNKS GENERATED : {len(chunks)}")
    print("=" * 80)


if __name__ == "__main__":
    main()