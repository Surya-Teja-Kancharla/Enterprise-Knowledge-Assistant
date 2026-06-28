"""
Enterprise Knowledge Assistant
Document Chunking Pipeline

Responsibilities
----------------
- Split document pages into semantic chunks
- Preserve document metadata
- Generate deterministic chunk IDs
- Prepare documents for embedding generation

This module intentionally DOES NOT:
- Generate embeddings
- Store vectors
- Perform retrieval
"""

from __future__ import annotations

import hashlib
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Dict, List


from app.core.config import settings
from app.core.logger import get_logger
from ingestion.parsers.loader import DocumentPage

logger = get_logger(__name__)

# ---------------------------------------------------------
# Separator Hierarchy
# ---------------------------------------------------------

SEPARATORS = [
    "\n\n",
    "\n•",
    "\n-",
    "\n",
    ". ",
    "? ",
    "! ",
    "; ",
    ", ",
    " ",
    "",
]


# ---------------------------------------------------------
# Simple Recursive Character Text Splitter
# ---------------------------------------------------------

class RecursiveCharacterTextSplitter:
    """
    Simple implementation of recursive character text splitting.
    """

    def __init__(
        self,
        chunk_size: int,
        chunk_overlap: int,
        separators: List[str],
        length_function: callable = len,
        keep_separator: bool = False,
        add_start_index: bool = False,
        strip_whitespace: bool = True,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators
        self.length_function = length_function
        self.keep_separator = keep_separator
        self.add_start_index = add_start_index
        self.strip_whitespace = strip_whitespace

    def create_documents(self, texts: List[str]) -> List["SplitDocument"]:
        """
        Split texts into chunks.
        """
        documents = []
        for text in texts:
            chunks = self._split_text(text, self.separators)
            for i, chunk in enumerate(chunks):
                if self.strip_whitespace:
                    chunk = chunk.strip()
                if chunk:
                    metadata = {}
                    if self.add_start_index:
                        metadata["start_index"] = text.find(chunk)
                    documents.append(SplitDocument(page_content=chunk, metadata=metadata))
        return documents

    def _split_text(self, text: str, separators: List[str]) -> List[str]:
        """
        Recursively split text using separators.
        """
        if not separators:
            return self._split_by_character(text)

        separator = separators[0]
        remaining_separators = separators[1:]

        # Handle empty separator as character fallback
        if separator == "":
            return self._split_by_character(text)

        splits = text.split(separator)
        final_chunks = []

        current_chunk = ""
        for split in splits:
            if self.length_function(current_chunk) + self.length_function(split) < self.chunk_size:
                if current_chunk:
                    current_chunk += separator if self.keep_separator else ""
                current_chunk += split
            else:
                if current_chunk:
                    if remaining_separators:
                        sub_chunks = self._split_text(current_chunk, remaining_separators)
                        final_chunks.extend(sub_chunks)
                    else:
                        final_chunks.append(current_chunk)
                    current_chunk = ""
                if self.length_function(split) < self.chunk_size:
                    current_chunk = split
                else:
                    if remaining_separators:
                        sub_chunks = self._split_text(split, remaining_separators)
                        final_chunks.extend(sub_chunks)
                    else:
                        final_chunks.append(split)

        if current_chunk:
            if remaining_separators:
                sub_chunks = self._split_text(current_chunk, remaining_separators)
                final_chunks.extend(sub_chunks)
            else:
                final_chunks.append(current_chunk)

        return self._merge_chunks(final_chunks)

    def _split_by_character(self, text: str) -> List[str]:
        """
        Fallback: split by character when no separators work.
        """
        chunks = []
        for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
            chunks.append(text[i:i + self.chunk_size])
        return chunks

    def _merge_chunks(self, chunks: List[str]) -> List[str]:
        """
        Apply overlap between chunks.
        """
        if self.chunk_overlap == 0:
            return chunks

        merged = []
        for i, chunk in enumerate(chunks):
            if i == 0:
                merged.append(chunk)
            else:
                overlap_start = max(0, len(chunk) - self.chunk_overlap)
                merged.append(chunk[overlap_start:])
        return merged


class SplitDocument:
    """
    Simple document class for split results.
    """

    def __init__(self, page_content: str, metadata: Dict[str, Any]):
        self.page_content = page_content
        self.metadata = metadata


# ---------------------------------------------------------
# Chunk Dataclass
# ---------------------------------------------------------

@dataclass(slots=True, frozen=True)
class DocumentChunk:
    """
    Represents one semantic chunk that will later be
    embedded and stored inside the vector database.
    """

    chunk_id: str

    text: str

    metadata: Dict[str, Any]


# ---------------------------------------------------------
# Chunker
# ---------------------------------------------------------

class DocumentChunker:
    """
    Splits DocumentPage objects into semantic chunks.

    Parameters
    ----------
    chunk_size
        Maximum chunk size.

    chunk_overlap
        Context overlap.

    Example
    -------
    chunker = DocumentChunker()

    chunks = chunker.chunk_documents(pages)
    """

    def __init__(
        self,
        chunk_size: int = settings.CHUNK_SIZE,
        chunk_overlap: int = settings.CHUNK_OVERLAP,
    ):

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size"
            )

        self.chunk_size = chunk_size

        self.chunk_overlap = chunk_overlap

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=SEPARATORS,
            length_function=len,
            keep_separator=False,
            add_start_index=True,
            strip_whitespace=True,
        )

        self.statistics = {
            "documents": 0,
            "pages": 0,
            "chunks": 0,
            "characters": 0,
            "average_chunk_size": 0,
            "largest_chunk": 0,
            "smallest_chunk": 0,
        }

        logger.info(
            "Chunker initialized "
            "(size=%d overlap=%d)",
            self.chunk_size,
            self.chunk_overlap,
        )

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    @staticmethod
    def _validate_page(
        page: DocumentPage,
    ) -> None:
        """
        Validate page object before chunking.
        """

        if not page.text.strip():
            raise ValueError(
                f"Page {page.page} "
                f"of {page.document} is empty."
            )

    # ---------------------------------------------------------
    # Chunk ID
    # ---------------------------------------------------------

    @staticmethod
    def _generate_chunk_id(
        document: str,
        page: int,
        chunk_number: int,
        text: str,
    ) -> str:
        """
        Generate deterministic chunk ID.

        Same document +
        same page +
        same chunk +
        same content

        always gives the same ID.
        """

        checksum = hashlib.md5(
            text.encode("utf-8")
        ).hexdigest()[:8]

        filename = (
            document
            .replace(".pdf", "")
            .replace(" ", "_")
            .lower()
        )

        return (
            f"{filename}"
            f"_p{page:03d}"
            f"_c{chunk_number:03d}"
            f"_{checksum}"
        )

    # ---------------------------------------------------------
    # Metadata
    # ---------------------------------------------------------

    def _build_chunk_metadata(
        self,
        page: DocumentPage,
        chunk_number: int,
    ) -> Dict[str, Any]:
        """
        Extend page metadata with chunk metadata.
        """

        metadata = deepcopy(page.metadata)

        metadata.update(
            {
                "chunk_number": chunk_number,
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.chunk_overlap,
            }
        )

        return metadata

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    def _update_statistics(
        self,
        chunk_length: int,
    ) -> None:
        """
        Update running statistics.
        """

        self.statistics["chunks"] += 1

        self.statistics["characters"] += chunk_length

        if (
            self.statistics["largest_chunk"]
            < chunk_length
        ):
            self.statistics["largest_chunk"] = chunk_length

        if (
            self.statistics["smallest_chunk"] == 0
            or chunk_length
            < self.statistics["smallest_chunk"]
        ):
            self.statistics["smallest_chunk"] = chunk_length

            # ---------------------------------------------------------
    # Single Page Chunking
    # ---------------------------------------------------------

    def _chunk_single_page(
        self,
        page: DocumentPage,
    ) -> List[DocumentChunk]:
        """
        Split a single page into semantic chunks.

        Parameters
        ----------
        page : DocumentPage

        Returns
        -------
        List[DocumentChunk]
        """

        self._validate_page(page)

        split_documents = self.splitter.create_documents(
            [page.text]
        )

        chunks: List[DocumentChunk] = []

        for chunk_index, split_doc in enumerate(
            split_documents,
            start=1,
        ):

            chunk_text = split_doc.page_content.strip()

            if not chunk_text:
                continue

            metadata = self._build_chunk_metadata(
                page,
                chunk_index,
            )

            chunk_id = self._generate_chunk_id(
                document=page.document,
                page=page.page,
                chunk_number=chunk_index,
                text=chunk_text,
            )

            metadata["chunk_id"] = chunk_id

            if "start_index" in split_doc.metadata:
                metadata["start_index"] = split_doc.metadata[
                    "start_index"
                ]

            chunk = DocumentChunk(
                chunk_id=chunk_id,
                text=chunk_text,
                metadata=metadata,
            )

            chunks.append(chunk)

            self._update_statistics(
                len(chunk_text)
            )

            logger.debug(
                "Created chunk %s (%d chars)",
                chunk_id,
                len(chunk_text),
            )

        return chunks

    # ---------------------------------------------------------
    # Multiple Page Chunking
    # ---------------------------------------------------------

    def chunk_documents(
        self,
        pages: List[DocumentPage],
    ) -> List[DocumentChunk]:
        """
        Chunk every page in the corpus.

        Parameters
        ----------
        pages : List[DocumentPage]

        Returns
        -------
        List[DocumentChunk]
        """

        logger.info(
            "Starting chunk generation..."
        )

        self.statistics["documents"] = len(
            {
                page.document
                for page in pages
            }
        )

        self.statistics["pages"] = len(pages)

        all_chunks: List[DocumentChunk] = []

        for page in pages:

            page_chunks = self._chunk_single_page(
                page
            )

            all_chunks.extend(page_chunks)

        if self.statistics["chunks"] > 0:

            self.statistics[
                "average_chunk_size"
            ] = round(
                self.statistics["characters"]
                / self.statistics["chunks"],
                2,
            )

        logger.info(
            "Chunk generation completed."
        )

        logger.info(
            "Generated %d chunks.",
            len(all_chunks),
        )

        return all_chunks

    # ---------------------------------------------------------
    # Chunk Preview
    # ---------------------------------------------------------

    @staticmethod
    def preview_chunk(
        chunk: DocumentChunk,
        length: int = 200,
    ) -> None:
        """
        Print a formatted preview of a chunk.
        """

        print("=" * 80)

        print(
            f"Chunk ID : {chunk.chunk_id}"
        )

        print(
            f"Document : {chunk.metadata['document']}"
        )

        print(
            f"Page : {chunk.metadata['page']}"
        )

        print(
            f"Chunk Number : {chunk.metadata['chunk_number']}"
        )

        print(
            f"Category : {chunk.metadata['category']}"
        )

        print()

        preview = (
            chunk.text[:length]
            .replace("\n", " ")
            .strip()
        )

        print(preview)

        print("=" * 80)

            # ---------------------------------------------------------
    # Statistics Reporting
    # ---------------------------------------------------------

    def get_statistics(self) -> Dict[str, Any]:
        """
        Return a copy of the current chunking statistics.

        Returns
        -------
        Dict[str, Any]
        """

        return deepcopy(self.statistics)

    def reset_statistics(self) -> None:
        """
        Reset all chunking statistics.

        Useful before processing a new corpus.
        """

        self.statistics = {
            "documents": 0,
            "pages": 0,
            "chunks": 0,
            "characters": 0,
            "average_chunk_size": 0,
            "largest_chunk": 0,
            "smallest_chunk": 0,
        }

        logger.info("Chunking statistics reset.")

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------

    def print_summary(self) -> None:
        """
        Print chunking summary.
        """

        logger.info("========== CHUNKING SUMMARY ==========")

        logger.info(
            "Documents Processed : %d",
            self.statistics["documents"],
        )

        logger.info(
            "Pages Processed : %d",
            self.statistics["pages"],
        )

        logger.info(
            "Chunks Generated : %d",
            self.statistics["chunks"],
        )

        logger.info(
            "Characters : %d",
            self.statistics["characters"],
        )

        logger.info(
            "Average Chunk Size : %.2f",
            self.statistics["average_chunk_size"],
        )

        logger.info(
            "Largest Chunk : %d",
            self.statistics["largest_chunk"],
        )

        logger.info(
            "Smallest Chunk : %d",
            self.statistics["smallest_chunk"],
        )

        logger.info("======================================")

    # ---------------------------------------------------------
    # Export
    # ---------------------------------------------------------

    def export_statistics(self) -> Dict[str, Any]:
        """
        Export statistics.

        This method is intended for dashboards,
        evaluation scripts and API responses.
        """

        return {
            "documents": self.statistics["documents"],
            "pages": self.statistics["pages"],
            "chunks": self.statistics["chunks"],
            "characters": self.statistics["characters"],
            "average_chunk_size": self.statistics[
                "average_chunk_size"
            ],
            "largest_chunk": self.statistics[
                "largest_chunk"
            ],
            "smallest_chunk": self.statistics[
                "smallest_chunk"
            ],
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
        }

    # ---------------------------------------------------------
    # Utility Methods
    # ---------------------------------------------------------

    def __len__(self) -> int:
        """
        Return number of chunks generated.
        """

        return self.statistics["chunks"]

    def __repr__(self) -> str:
        """
        Developer-friendly representation.
        """

        return (
            "DocumentChunker("
            f"chunk_size={self.chunk_size}, "
            f"chunk_overlap={self.chunk_overlap}, "
            f"chunks={self.statistics['chunks']}"
            ")"
        )