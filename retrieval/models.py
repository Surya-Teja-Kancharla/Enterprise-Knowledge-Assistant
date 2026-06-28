"""
Enterprise Knowledge Assistant
Retrieval Models

Defines strongly-typed objects used by the retrieval layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ==========================================================
# Retrieved Chunk
# ==========================================================

@dataclass(slots=True, frozen=True)
class RetrievedChunk:
    """
    Represents a chunk returned from the vector database.
    """

    chunk_id: str

    text: str

    score: float

    metadata: dict[str, Any]

    document: str

    page: int

    category: str

    source: str

    chunk_number: int

    def to_dict(self) -> dict[str, Any]:
        """
        Convert object to dictionary.
        """

        return {
            "chunk_id": self.chunk_id,
            "text": self.text,
            "score": self.score,
            "document": self.document,
            "page": self.page,
            "category": self.category,
            "source": self.source,
            "chunk_number": self.chunk_number,
            "metadata": self.metadata,
        }


# ==========================================================
# Retrieval Response
# ==========================================================

@dataclass(slots=True)
class RetrievalResponse:
    """
    Complete retrieval response.
    """

    query: str

    retrieved_chunks: list[RetrievedChunk] = field(default_factory=list)

    search_type: str = "mmr"

    top_k: int = 5

    latency_ms: float = 0.0

    total_candidates: int = 0

    average_score: float = 0.0

    def add_chunk(
        self,
        chunk: RetrievedChunk,
    ) -> None:
        """
        Append a retrieved chunk.
        """

        self.retrieved_chunks.append(chunk)

    @property
    def result_count(self) -> int:
        """
        Number of retrieved chunks.
        """

        return len(self.retrieved_chunks)

    def calculate_average_score(self) -> None:
        """
        Compute mean similarity score.
        """

        if not self.retrieved_chunks:
            self.average_score = 0.0
            return

        self.average_score = round(
            sum(chunk.score for chunk in self.retrieved_chunks)
            / len(self.retrieved_chunks),
            4,
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize response.
        """

        return {
            "query": self.query,
            "search_type": self.search_type,
            "top_k": self.top_k,
            "latency_ms": self.latency_ms,
            "total_candidates": self.total_candidates,
            "average_score": self.average_score,
            "result_count": self.result_count,
            "results": [
                chunk.to_dict()
                for chunk in self.retrieved_chunks
            ],
        }
