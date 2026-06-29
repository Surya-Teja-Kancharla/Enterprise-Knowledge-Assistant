"""
Enterprise Knowledge Assistant
Hybrid Retrieval Merger
"""

from __future__ import annotations

import logging

from typing import Dict
from typing import List

from langchain_core.documents import Document


logger = logging.getLogger(__name__)


class HybridMerger:
    """
    Merge BM25 and Vector retrieval results
    using Reciprocal Rank Fusion (RRF).
    """

    def __init__(
        self,
        rrf_k: int = 60,
    ) -> None:
        self.rrf_k = rrf_k

        logger.info(
            "HybridMerger initialized (RRF k=%d)",
            rrf_k,
        )

    @staticmethod
    def _document_id(document: Document) -> str:
        """
        Unique identifier for duplicate removal.
        """

        metadata = document.metadata

        return (
            metadata.get("chunk_id")
            or metadata.get("id")
            or (
                f"{metadata.get('document', '')}"
                f"_{metadata.get('page', '')}"
                f"_{metadata.get('chunk', '')}"
            )
        )

    def merge(
        self,
        vector_results: List[Document],
        bm25_results: List[Document],
        top_k: int = 5,
    ) -> List[Document]:
        """
        Merge two ranked lists using
        Reciprocal Rank Fusion.
        """

        logger.info("Running hybrid merge...")

        scores: Dict[str, float] = {}
        documents: Dict[str, Document] = {}

        #
        # Vector retrieval
        #
        for rank, document in enumerate(vector_results, start=1):

            doc_id = self._document_id(document)

            scores.setdefault(doc_id, 0.0)

            scores[doc_id] += 1 / (self.rrf_k + rank)

            documents[doc_id] = document

        #
        # BM25 retrieval
        #
        for rank, document in enumerate(bm25_results, start=1):

            doc_id = self._document_id(document)

            scores.setdefault(doc_id, 0.0)

            scores[doc_id] += 1 / (self.rrf_k + rank)

            documents[doc_id] = document

        ranked = sorted(
            scores.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        merged = [
            documents[doc_id]
            for doc_id, _ in ranked[:top_k]
        ]

        logger.info(
            "Hybrid merge completed (%d results).",
            len(merged),
        )

        return merged
