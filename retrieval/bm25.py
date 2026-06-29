"""
Enterprise Knowledge Assistant
BM25 Keyword Retrieval
"""

from __future__ import annotations

import logging
import re

from typing import List

from langchain_core.documents import Document
from rank_bm25 import BM25Okapi


logger = logging.getLogger(__name__)


class BM25Retriever:
    """
    Lightweight BM25 keyword retriever.

    Builds an in-memory BM25 index from LangChain Documents.
    """

    def __init__(self, documents: List[Document]) -> None:
        self.documents = documents

        self.tokenized_corpus = [
            self._tokenize(doc.page_content)
            for doc in documents
        ]

        self.index = BM25Okapi(self.tokenized_corpus)

        logger.info("========== BM25 SUMMARY ==========")
        logger.info("Indexed Documents : %d", len(self.documents))
        logger.info("Indexed Chunks    : %d", len(self.tokenized_corpus))
        logger.info("==================================")

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """
        Basic tokenizer.

        Lowercases text and extracts alphanumeric tokens.
        """

        return re.findall(r"\b\w+\b", text.lower())

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> List[Document]:
        """
        Retrieve top-k documents using BM25.
        """

        logger.info("Running BM25 retrieval...")

        query_tokens = self._tokenize(query)

        scores = self.index.get_scores(query_tokens)

        ranked = sorted(
            zip(self.documents, scores),
            key=lambda x: x[1],
            reverse=True,
        )

        results = [
            document
            for document, score in ranked[:top_k]
            if score > 0
        ]

        logger.info(
            "Retrieved %d BM25 documents.",
            len(results),
        )

        return results
