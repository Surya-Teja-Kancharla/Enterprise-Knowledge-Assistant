"""
Enterprise Knowledge Assistant

Vector Store Models

Contains immutable data models used by the
vector indexing and retrieval pipeline.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Dict, List


# ==========================================================
# Search Result
# ==========================================================

@dataclass(slots=True, frozen=True)
class SearchResult:
    """
    Represents a semantic search result returned
    from the vector database.
    """

    chunk_id: str

    score: float

    text: str

    metadata: Dict[str, Any]

    @property
    def document(self) -> str:
        """
        Return source document name.
        """

        return self.metadata.get(
            "document",
            "",
        )

    @property
    def page(self) -> int:
        """
        Return page number.
        """

        return self.metadata.get(
            "page",
            0,
        )

    @property
    def category(self) -> str:
        """
        Return document category.
        """

        return self.metadata.get(
            "category",
            "",
        )

    def to_json(self) -> Dict[str, Any]:
        """
        Serialize search result.
        """

        return {

            "chunk_id": self.chunk_id,

            "score": self.score,

            "text": self.text,

            "metadata": deepcopy(
                self.metadata
            ),

        }


# ==========================================================
# Index Statistics
# ==========================================================

@dataclass(slots=True)
class IndexStatistics:
    """
    Runtime statistics for the vector index.
    """

    indexed_vectors: int = 0

    documents: int = 0

    batches: int = 0

    duplicates: int = 0

    queries: int = 0

    collection_size: int = 0

    def reset(self) -> None:
        """
        Reset statistics.
        """

        self.indexed_vectors = 0
        self.documents = 0
        self.batches = 0
        self.duplicates = 0
        self.queries = 0
        self.collection_size = 0

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert statistics to dictionary.
        """

        return {

            "indexed_vectors":
                self.indexed_vectors,

            "documents":
                self.documents,

            "batches":
                self.batches,

            "duplicates":
                self.duplicates,

            "queries":
                self.queries,

            "collection_size":
                self.collection_size,

        }


# ==========================================================
# Search Response
# ==========================================================

@dataclass(slots=True, frozen=True)
class SearchResponse:
    """
    Represents a complete retrieval response.
    """

    query: str

    total_results: int

    results: List[SearchResult]

    def to_json(self) -> Dict[str, Any]:
        """
        Serialize response.
        """

        return {

            "query": self.query,

            "total_results":
                self.total_results,

            "results": [

                result.to_json()

                for result in self.results

            ],

        }

    def __len__(self) -> int:
        """
        Number of retrieved results.
        """

        return len(self.results)