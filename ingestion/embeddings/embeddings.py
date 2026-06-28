"""
Enterprise Knowledge Assistant
Embedding Generation Pipeline

Responsibilities
----------------
- Generate embeddings using local BGE model
- Batch embedding requests
- Preserve chunk metadata
- Validate embedding dimensions
- Prepare vectors for vector database ingestion

This module intentionally DOES NOT:
- Store vectors
- Perform retrieval
- Query LLMs
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List

from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.core.logger import get_logger
from ingestion.chunking.chunker import DocumentChunk
from ingestion.embeddings.models import EmbeddedChunk

logger = get_logger(__name__)


# ---------------------------------------------------------
# Embedding Generator
# ---------------------------------------------------------

class EmbeddingGenerator:
    """
    Generates embeddings using local BGE model.

    Example
    -------
    generator = EmbeddingGenerator()

    vectors = generator.generate_embeddings(chunks)
    """

    def __init__(self):

        self.model = settings.EMBEDDING_MODEL

        self.batch_size = settings.EMBEDDING_BATCH_SIZE

        self.vector_dimension = settings.VECTOR_DIMENSION

        logger.info(
            "Loading embedding model: %s",
            self.model,
        )

        self.model_instance = SentenceTransformer(
            self.model
        )

        self.statistics = {
            "chunks": 0,
            "embedded_chunks": 0,
            "failed_chunks": 0,
            "embedding_dimension": self.vector_dimension,
        }

        logger.info(
            "Embedding generator initialized."
        )

        logger.info(
            "Model : %s",
            self.model,
        )

        logger.info(
            "Batch Size : %d",
            self.batch_size,
        )

        logger.info(
            "Vector Dimension : %d",
            self.vector_dimension,
        )

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    @staticmethod
    def _validate_chunk(
        chunk: DocumentChunk,
    ) -> None:

        if not chunk.text.strip():

            raise ValueError(
                f"{chunk.chunk_id} has empty text."
            )

    # ---------------------------------------------------------
    # Batch Generator
    # ---------------------------------------------------------

    def _batch_chunks(
        self,
        chunks: List[DocumentChunk],
    ) -> List[List[DocumentChunk]]:
        """
        Split chunks into batches.
        """

        batches = []

        for i in range(
            0,
            len(chunks),
            self.batch_size,
        ):

            batches.append(
                chunks[i : i + self.batch_size]
            )

        return batches

    # ---------------------------------------------------------
    # Metadata
    # ---------------------------------------------------------

    @staticmethod
    def _copy_metadata(
        chunk: DocumentChunk,
    ) -> Dict[str, Any]:

        return deepcopy(chunk.metadata)

    # ---------------------------------------------------------
    # Dimension Validation
    # ---------------------------------------------------------

    def _validate_dimension(
        self,
        embedding: List[float],
    ) -> None:

        if len(embedding) != self.vector_dimension:

            raise ValueError(
                f"Expected embedding dimension "
                f"{self.vector_dimension}, "
                f"received {len(embedding)}"
            )

        # ---------------------------------------------------------
    # Local Embedding Generation
    # ---------------------------------------------------------

    def _embed_batch(
        self,
        batch: List[DocumentChunk],
    ) -> List[EmbeddedChunk]:
        """
        Generate embeddings for a single batch of chunks.

        Parameters
        ----------
        batch : List[DocumentChunk]

        Returns
        -------
        List[EmbeddedChunk]
        """

        texts = [chunk.text for chunk in batch]

        try:

            embeddings = self.model_instance.encode(
                texts,
                normalize_embeddings=True,
                convert_to_numpy=True,
                show_progress_bar=False,
            )

            embedded_chunks: List[EmbeddedChunk] = []

            for chunk, embedding in zip(
                batch,
                embeddings,
            ):

                embedding_list = embedding.tolist()

                self._validate_dimension(
                    embedding_list
                )

                embedded_chunks.append(
                    EmbeddedChunk(
                        chunk_id=chunk.chunk_id,
                        text=chunk.text,
                        embedding=embedding_list,
                        metadata=self._copy_metadata(
                            chunk
                        ),
                    )
                )

                self.statistics[
                    "embedded_chunks"
                ] += 1

            return embedded_chunks

        except Exception as exc:

            logger.error(
                "Embedding batch failed: %s",
                exc,
            )

            self.statistics[
                "failed_chunks"
            ] += len(batch)

            raise

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def generate_embeddings(
        self,
        chunks: List[DocumentChunk],
    ) -> List[EmbeddedChunk]:
        """
        Generate embeddings for all document chunks.

        Parameters
        ----------
        chunks : List[DocumentChunk]

        Returns
        -------
        List[EmbeddedChunk]
        """

        logger.info(
            "Generating embeddings..."
        )

        self.statistics["chunks"] = len(chunks)

        embedded_documents: List[
            EmbeddedChunk
        ] = []

        batches = self._batch_chunks(
            chunks
        )

        logger.info(
            "Created %d batches.",
            len(batches),
        )

        for batch_number, batch in enumerate(
            batches,
            start=1,
        ):

            logger.info(
                "Embedding batch %d/%d "
                "(%d chunks)",
                batch_number,
                len(batches),
                len(batch),
            )

            for chunk in batch:

                self._validate_chunk(
                    chunk
                )

            vectors = self._embed_batch(
                batch
            )

            embedded_documents.extend(
                vectors
            )

        logger.info(
            "Embedding generation completed."
        )

        logger.info(
            "Generated %d embeddings.",
            len(embedded_documents),
        )

        return embedded_documents

    # ---------------------------------------------------------
    # Preview
    # ---------------------------------------------------------

    @staticmethod
    def preview_embedding(
        embedded: EmbeddedChunk,
        values: int = 8,
    ) -> None:
        """
        Print embedding preview.
        """

        print("=" * 80)

        print(
            f"Chunk ID : {embedded.chunk_id}"
        )

        print(
            f"Document : "
            f"{embedded.metadata['document']}"
        )

        print(
            f"Page : "
            f"{embedded.metadata['page']}"
        )

        print(
            f"Category : "
            f"{embedded.metadata['category']}"
        )

        print()

        print(
            "Embedding Dimension :",
            len(embedded.embedding),
        )

        print()

        print(
            "First Values :"
        )

        print(
            embedded.embedding[:values]
        )

        print("=" * 80)


        # ---------------------------------------------------------
    # Statistics Reporting
    # ---------------------------------------------------------

    def get_statistics(self) -> Dict[str, Any]:
        """
        Return a copy of the embedding statistics.

        Returns
        -------
        Dict[str, Any]
        """

        return deepcopy(self.statistics)

    def reset_statistics(self) -> None:
        """
        Reset all embedding statistics.

        Useful before embedding a new corpus.
        """

        self.statistics = {
            "chunks": 0,
            "embedded_chunks": 0,
            "failed_chunks": 0,
            "embedding_dimension": self.vector_dimension,
        }

        logger.info("Embedding statistics reset.")

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------

    def print_summary(self) -> None:
        """
        Print embedding generation summary.
        """

        logger.info(
            "========== EMBEDDING SUMMARY =========="
        )

        logger.info(
            "Chunks Received : %d",
            self.statistics["chunks"],
        )

        logger.info(
            "Embeddings Generated : %d",
            self.statistics["embedded_chunks"],
        )

        logger.info(
            "Failed Chunks : %d",
            self.statistics["failed_chunks"],
        )

        logger.info(
            "Embedding Dimension : %d",
            self.statistics["embedding_dimension"],
        )

        logger.info(
            "======================================="
        )

    # ---------------------------------------------------------
    # Export
    # ---------------------------------------------------------

    def export_statistics(self) -> Dict[str, Any]:
        """
        Export statistics for dashboards,
        evaluation scripts or APIs.
        """

        return {
            "chunks": self.statistics["chunks"],
            "embedded_chunks": self.statistics[
                "embedded_chunks"
            ],
            "failed_chunks": self.statistics[
                "failed_chunks"
            ],
            "embedding_dimension": self.statistics[
                "embedding_dimension"
            ],
            "model": self.model,
            "batch_size": self.batch_size,
        }

    # ---------------------------------------------------------
    # Utility Methods
    # ---------------------------------------------------------

    def __len__(self) -> int:
        """
        Return the number of successfully embedded chunks.
        """

        return self.statistics[
            "embedded_chunks"
        ]

    def __repr__(self) -> str:
        """
        Developer-friendly representation.
        """

        return (
            "EmbeddingGenerator("
            f"model='{self.model}', "
            f"batch_size={self.batch_size}, "
            f"embedded_chunks="
            f"{self.statistics['embedded_chunks']}"
            ")"
        )

  
