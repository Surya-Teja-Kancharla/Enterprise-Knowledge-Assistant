"""
Enterprise Knowledge Assistant
Hybrid Retriever

Combines:

1. ChromaDB Semantic Search (MMR)
2. BM25 Keyword Search
3. Reciprocal Rank Fusion (RRF)
"""

from __future__ import annotations

import logging

from typing import List

from langchain_core.documents import Document

from retrieval.bm25 import BM25Retriever
from retrieval.merger import HybridMerger


logger = logging.getLogger(__name__)


class HybridRetriever:
    """
    Enterprise Hybrid Retriever.

    Retrieval Pipeline

    Query
        │
        ├─────────────► Vector Search
        │
        ├─────────────► BM25 Search
        │
        ▼
    Reciprocal Rank Fusion
        │
        ▼
      Top-K Results
    """

    def __init__(
        self,
        vector_retriever,
        documents: List[Document],
        top_k: int = 5,
    ) -> None:

        self.vector_retriever = vector_retriever

        self.top_k = top_k

        self.bm25 = BM25Retriever(documents)

        self.merger = HybridMerger()

        logger.info(
            "HybridRetriever initialized."
        )

    # ----------------------------------------------------------
    # Vector Search
    # ----------------------------------------------------------

    def _vector_search(
        self,
        query: str,
    ) -> List[Document]:

        logger.info("Running semantic search...")

        return self.vector_retriever.invoke(query)

    # ----------------------------------------------------------
    # BM25 Search
    # ----------------------------------------------------------

    def _keyword_search(
        self,
        query: str,
    ) -> List[Document]:

        logger.info("Running keyword search...")

        return self.bm25.retrieve(
            query=query,
            top_k=self.top_k,
        )

    # ----------------------------------------------------------
    # Hybrid Search
    # ----------------------------------------------------------

    def retrieve(
        self,
        query: str,
    ) -> List[Document]:

        logger.info(
            "========== HYBRID SEARCH =========="
        )

        logger.info(
            "Query : %s",
            query,
        )

        vector_results = self._vector_search(
            query
        )

        bm25_results = self._keyword_search(
            query
        )

        merged = self.merger.merge(
            vector_results=vector_results,
            bm25_results=bm25_results,
            top_k=self.top_k,
        )

        logger.info(
            "Hybrid retrieval completed."
        )

        logger.info(
            "Returned %d documents.",
            len(merged),
        )

        logger.info(
            "=================================="
        )

        return merged
