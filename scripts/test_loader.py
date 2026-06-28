"""
Simple executable script to test the PDF loader.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import settings
from app.core.logger import configure_logger
from ingestion.parsers.loader import PDFLoader


def main() -> None:

    configure_logger()

    loader = PDFLoader(settings.RAW_DATA_PATH)

    pages = loader.load_documents()

    loader.print_summary()

    print("\n")

    print("=" * 80)

    print("FIRST FIVE EXTRACTED PAGES")

    print("=" * 80)

    for page in pages[:5]:

        print(f"Document : {page.document}")

        print(f"Page     : {page.page}")

        print(f"Category : {page.metadata['category']}")

        print(f"Characters : {len(page.text)}")

        preview = page.text[:250].replace("\n", " ")

        print(f"Preview  : {preview}")

        print("-" * 80)

    print("\n")

    print("=" * 80)

    print(f"TOTAL DOCUMENT PAGES LOADED : {len(pages)}")

    print("=" * 80)


if __name__ == "__main__":
    main()