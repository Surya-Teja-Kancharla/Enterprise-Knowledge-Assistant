"""
Enterprise Knowledge Assistant
PDF Document Loader

Responsibilities:
- Discover PDF documents
- Load PDFs using PyMuPDF
- Extract page-wise text
- Clean extracted text
- Generate metadata
- Return structured DocumentPage objects

This module intentionally DOES NOT:
- Chunk text
- Generate embeddings
- Index into a vector database
"""

from __future__ import annotations

from app.core.config import settings
from app.core.logger import get_logger
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import fitz


logger = get_logger(__name__)


@dataclass(slots=True)
class DocumentPage:
    """
    Represents a single page extracted from a PDF.
    """

    document: str
    page: int
    text: str
    metadata: Dict[str, Any]


class PDFLoader:
    """
    Production-ready PDF loader.

    Example
    -------
    loader = PDFLoader(settings.RAW_DATA_PATH)
    pages = loader.load_documents()
    """

    SUPPORTED_EXTENSION = ".pdf"

    def __init__(self, data_directory: str | Path):
        self.data_directory = Path(data_directory)

        if not self.data_directory.exists():
            raise FileNotFoundError(
                f"Directory does not exist: {self.data_directory}"
            )

        self.statistics = {
            "documents": 0,
            "pages": 0,
            "characters": 0,
            "largest_document": "",
            "largest_document_pages": 0,
            "average_page_length": 0,
        }

    # --------------------------------------------------------
    # Public API
    # --------------------------------------------------------

    def load_documents(self) -> List[DocumentPage]:
        """
        Discover all PDFs and load them.

        Returns
        -------
        List[DocumentPage]
        """

        pdf_files = self._discover_pdfs()

        logger.info("Found %d PDF(s).", len(pdf_files))

        pages: List[DocumentPage] = []

        for pdf_path in pdf_files:
            pages.extend(self._load_single_pdf(pdf_path))

        self._calculate_statistics(pages)

        return pages

    # --------------------------------------------------------
    # Discovery
    # --------------------------------------------------------

    def _discover_pdfs(self) -> List[Path]:
        """
        Recursively discover PDF files.
        """

        pdfs = sorted(
            self.data_directory.rglob(f"*{self.SUPPORTED_EXTENSION}")
        )

        return pdfs

    # --------------------------------------------------------
    # Loading
    # --------------------------------------------------------

    def _load_single_pdf(
        self,
        pdf_path: Path,
    ) -> List[DocumentPage]:

        logger.info("Loading %s", pdf_path.name)

        extracted_pages: List[DocumentPage] = []

        try:

            pdf = fitz.open(pdf_path)

        except Exception as exc:

            logger.exception(
                "Failed to open %s : %s",
                pdf_path.name,
                exc,
            )

            return extracted_pages

        total_pages = pdf.page_count

        logger.info(
            "%s contains %d pages",
            pdf_path.name,
            total_pages,
        )

        self.statistics["documents"] += 1

        if total_pages > self.statistics["largest_document_pages"]:

            self.statistics["largest_document_pages"] = total_pages
            self.statistics["largest_document"] = pdf_path.name

        for page_index in range(total_pages):

            page = pdf.load_page(page_index)

            raw_text = page.get_text("text")

            cleaned = self._clean_text(raw_text)

            metadata = self._build_metadata(
                pdf_path,
                page_index + 1,
            )

            extracted_pages.append(
                DocumentPage(
                    document=pdf_path.name,
                    page=page_index + 1,
                    text=cleaned,
                    metadata=metadata,
                )
            )

            logger.debug(
                "Extracted page %d from %s",
                page_index + 1,
                pdf_path.name,
            )

        pdf.close()

        logger.info(
            "Finished %s",
            pdf_path.name,
        )

        return extracted_pages

    # --------------------------------------------------------
    # Cleaning
    # --------------------------------------------------------

    @staticmethod
    def _clean_text(text: str) -> str:
        """
        Remove unnecessary whitespace while preserving
        punctuation and casing.
        """

        if not text:
            return ""

        text = text.replace("\t", " ")

        text = re.sub(r"[ ]{2,}", " ", text)

        text = re.sub(r"\n{3,}", "\n\n", text)

        text = "\n".join(
            line.strip()
            for line in text.splitlines()
        )

        return text.strip()

    # --------------------------------------------------------
    # Metadata
    # --------------------------------------------------------

    def _build_metadata(
        self,
        pdf_path: Path,
        page: int,
    ) -> Dict[str, Any]:

        try:
            category = pdf_path.parent.name
        except Exception:
            category = "unknown"

        return {
            "document": pdf_path.name,
            "page": page,
            "source": str(pdf_path),
            "category": category,
        }

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    def _calculate_statistics(
        self,
        pages: List[DocumentPage],
    ) -> None:

        page_count = len(pages)

        character_count = sum(
            len(page.text)
            for page in pages
        )

        average = (
            character_count / page_count
            if page_count
            else 0
        )

        self.statistics["pages"] = page_count
        self.statistics["characters"] = character_count
        self.statistics["average_page_length"] = round(
            average,
            2,
        )

    # --------------------------------------------------------
    # Reporting
    # --------------------------------------------------------

    def print_summary(self) -> None:

        logger.info("========== LOADER SUMMARY ==========")

        logger.info(
            "Documents Loaded : %d",
            self.statistics["documents"],
        )

        logger.info(
            "Pages Loaded : %d",
            self.statistics["pages"],
        )

        logger.info(
            "Characters : %d",
            self.statistics["characters"],
        )

        logger.info(
            "Average Page Length : %.2f",
            self.statistics["average_page_length"],
        )

        logger.info(
            "Largest Document : %s (%d pages)",
            self.statistics["largest_document"],
            self.statistics["largest_document_pages"],
        )

        logger.info("===================================")