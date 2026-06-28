"""
Enterprise Knowledge Assistant
Embedding Models

Contains immutable data models used throughout
the embedding and indexing pipeline.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(slots=True, frozen=True)
class VectorRecord:
    """
    Generic vector record.

    Independent of any vector database.
    """

    id: str

    document: str

    embedding: List[float]

    metadata: Dict[str, Any]


@dataclass(slots=True, frozen=True)
class EmbeddedChunk:
    """
    Represents a document chunk together with
    its embedding vector.
    """

    chunk_id: str

    text: str

    embedding: List[float]

    metadata: Dict[str, Any]

    @property
    def dimension(self) -> int:
        """
        Return embedding dimension.
        """

        return len(self.embedding)

    def to_vector_record(self) -> VectorRecord:
        """
        Convert into a generic vector record.
        """

        return VectorRecord(
            id=self.chunk_id,
            document=self.text,
            embedding=self.embedding,
            metadata=deepcopy(self.metadata),
        )

    def to_chroma_record(self) -> Dict[str, Any]:
        """
        Convert to ChromaDB format.
        """

        return {
            "ids": [self.chunk_id],
            "documents": [self.text],
            "embeddings": [self.embedding],
            "metadatas": [deepcopy(self.metadata)],
        }

    def to_json(self) -> Dict[str, Any]:
        """
        Serialize object.
        """

        return {
            "chunk_id": self.chunk_id,
            "text": self.text,
            "embedding_dimension": len(
                self.embedding
            ),
            "metadata": deepcopy(self.metadata),
        }
