"""
Enterprise Knowledge Assistant

Vector Database Indexer

Responsibilities
----------------
- Initialize persistent ChromaDB
- Create or load collections
- Validate vector records
- Batch vector operations
- Maintain indexing statistics

This module intentionally DOES NOT:
- Generate embeddings
- Chunk documents
- Call LLMs
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List

import chromadb
from chromadb import PersistentClient
from chromadb.api.models.Collection import Collection

from app.core.config import settings
from app.core.logger import get_logger

from ingestion.embeddings.models import (
    EmbeddedChunk,
    VectorRecord,
)

from ingestion.vector_store.models import (
    SearchResult,
    IndexStatistics,
    SearchResponse,
)

logger = get_logger(__name__)


# ==========================================================
# Vector Indexer
# ==========================================================

class VectorIndexer:
    """
    Production-ready ChromaDB indexer.

    Example
    -------
    indexer = VectorIndexer()

    indexer.index_documents(embedded_chunks)
    """

    def __init__(self):

        self.persist_directory = Path(
            settings.VECTOR_DB_PATH
        )

        self.persist_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.collection_name = (
            settings.VECTOR_COLLECTION_NAME
        )

        self.batch_size = (
            settings.INDEX_BATCH_SIZE
        )

        logger.info(
            "Initializing ChromaDB..."
        )

        self.client: PersistentClient = (
            PersistentClient(
                path=str(
                    self.persist_directory
                )
            )
        )

        self.collection = (
            self._load_collection()
        )

        self.statistics = {

            "indexed_vectors": 0,

            "documents": 0,

            "batches": 0,

            "queries": 0,

            "duplicates": 0,

            "collection_size": 0,

        }

        logger.info(
            "Collection : %s",
            self.collection_name,
        )

        logger.info(
            "Persistence : %s",
            self.persist_directory,
        )

        logger.info(
            "Batch Size : %d",
            self.batch_size,
        )

    # ==========================================================
    # Collection
    # ==========================================================

    def _load_collection(
        self,
    ) -> Collection:
        """
        Create or load Chroma collection.
        """

        logger.info(
            "Loading collection..."
        )

        collection = (
            self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={
                    "hnsw:space": settings.VECTOR_DISTANCE,
                },
            )
        )

        logger.info(
            "Collection ready."
        )

        return collection

    # ==========================================================
    # Validation
    # ==========================================================

    @staticmethod
    def _validate_record(
        record: VectorRecord,
    ) -> None:
        """
        Validate vector record.
        """

        if not record.id:

            raise ValueError(
                "Vector id cannot be empty."
            )

        if not record.document.strip():

            raise ValueError(
                f"{record.id} contains empty text."
            )

        if not record.embedding:

            raise ValueError(
                f"{record.id} contains no embedding."
            )

        if not record.metadata:

            raise ValueError(
                f"{record.id} contains no metadata."
            )

    # ==========================================================
    # Conversion
    # ==========================================================

    @staticmethod
    def _prepare_records(
        embedded_chunks: List[
            EmbeddedChunk
        ],
    ) -> List[VectorRecord]:
        """
        Convert EmbeddedChunks into
        VectorRecords.
        """

        return [

            chunk.to_vector_record()

            for chunk in embedded_chunks

        ]

    # ==========================================================
    # Batch Generator
    # ==========================================================

    def _batch_records(
        self,
        records: List[
            VectorRecord
        ],
    ) -> List[
        List[VectorRecord]
    ]:
        """
        Split records into batches.
        """

        batches = []

        for start in range(
            0,
            len(records),
            self.batch_size,
        ):

            batches.append(

                records[
                    start:
                    start + self.batch_size
                ]

            )

        return batches

    # ==========================================================
    # Existing IDs
    # ==========================================================

    def _existing_ids(
        self,
    ) -> set[str]:
        """
        Return all indexed ids.

        Used to prevent duplicate inserts.
        """

        ids = self.collection.get(
            include=[]
        )["ids"]

        return set(ids)

    # ==========================================================
    # Statistics
    # ==========================================================

    def get_statistics(
        self,
    ) -> Dict[str, Any]:
        """
        Return current statistics.
        """

        self.statistics[
            "collection_size"
        ] = self.collection.count()

        return deepcopy(
            self.statistics
        )

    # ==========================================================
    # Indexing
    # ==========================================================

    def index_documents(
        self,
        embedded_chunks: List[EmbeddedChunk],
    ) -> None:
        """
        Index embedded document chunks into ChromaDB.

        Parameters
        ----------
        embedded_chunks : List[EmbeddedChunk]
        """

        if not embedded_chunks:
            logger.warning("No embedded chunks supplied.")
            return

        logger.info(
            "Preparing %d embedded chunks for indexing...",
            len(embedded_chunks),
        )

        records = self._prepare_records(embedded_chunks)
        existing_ids = self._existing_ids()
        new_records: List[VectorRecord] = []

        for record in records:
            self._validate_record(record)

            if record.id in existing_ids:
                self.statistics["duplicates"] += 1
                logger.debug("Skipping duplicate: %s", record.id)
                continue

            new_records.append(record)

        logger.info("%d new vectors to index.", len(new_records))

        batches = self._batch_records(new_records)
        logger.info("Created %d indexing batches.", len(batches))

        for batch_number, batch in enumerate(batches, start=1):
            logger.info(
                "Indexing batch %d/%d (%d vectors)",
                batch_number,
                len(batches),
                len(batch),
            )
            self._upsert_batch(batch)
            self.statistics["batches"] += 1

        self.statistics["indexed_vectors"] += len(new_records)
        self.statistics["documents"] = len(
            {record.metadata["document"] for record in new_records}
        )
        self.statistics["collection_size"] = self.collection.count()

        logger.info("Indexing completed.")
        logger.info(
            "Collection contains %d vectors.",
            self.statistics["collection_size"],
        )

    # ==========================================================
    # Batch Upsert
    # ==========================================================

    def _upsert_batch(
        self,
        batch: List[VectorRecord],
    ) -> None:
        """
        Upsert a batch of vectors into ChromaDB.
        """

        ids = []
        documents = []
        embeddings = []
        metadatas = []

        for record in batch:
            ids.append(record.id)
            documents.append(record.document)
            embeddings.append(record.embedding)
            metadatas.append(deepcopy(record.metadata))

        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    # ==========================================================
    # Collection Information
    # ==========================================================

    def count(self) -> int:
        """
        Return the number of vectors currently stored in the collection.
        """
        return self.collection.count()

    def collection_exists(self) -> bool:
        """
        Check whether the collection exists.
        """
        collections = self.client.list_collections()
        return any(
            collection.name == self.collection_name
            for collection in collections
        )

    # ==========================================================
    # Persistence
    # ==========================================================

    def persist(self) -> None:
        """
        Persist the vector database.

        Modern ChromaDB persists automatically,
        but this method is retained for API compatibility.
        """
        logger.info("Vector database persisted.")

    # ==========================================================
    # Export
    # ==========================================================

    def export_statistics(self) -> Dict[str, Any]:
        """
        Export statistics.
        """
        return {
            "collection": self.collection_name,
            "vectors": self.collection.count(),
            "indexed_vectors": self.statistics["indexed_vectors"],
            "duplicates": self.statistics["duplicates"],
            "documents": self.statistics["documents"],
            "batches": self.statistics["batches"],
            "queries": self.statistics["queries"],
            "storage": str(self.persist_directory),
        }

    # ==========================================================
    # Collection Management
    # ==========================================================

    def reset_collection(self) -> None:
        """
        Remove all vectors while preserving
        the collection.
        """

        logger.warning(
            "Resetting collection '%s'...",
            self.collection_name,
        )

        self.client.delete_collection(
            self.collection_name
        )

        self.collection = (
            self._load_collection()
        )

        self.reset_statistics()

        logger.info(
            "Collection reset completed."
        )

    def delete_collection(self) -> None:
        """
        Delete the collection permanently.
        """

        logger.warning(
            "Deleting collection '%s'...",
            self.collection_name,
        )

        self.client.delete_collection(
            self.collection_name
        )

        logger.info(
            "Collection deleted."
        )

    # ==========================================================
    # Query Methods
    # ==========================================================

    def list_documents(self) -> List[str]:
        """
        Return list of unique document names in the collection.
        """
        result = self.collection.get(include=["metadatas"])
        documents = {
            metadata["document"]
            for metadata in result["metadatas"]
            if "document" in metadata
        }
        return sorted(list(documents))

    def list_categories(self) -> List[str]:
        """
        Return list of unique categories in the collection.
        """
        result = self.collection.get(include=["metadatas"])
        categories = {
            metadata["category"]
            for metadata in result["metadatas"]
            if "category" in metadata
        }
        return sorted(list(categories))

    def similarity_search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
    ) -> List[SearchResult]:
        """
        Perform similarity search using query embedding.

        Parameters
        ----------
        query_embedding : List[float]
            The embedding of the query text.
        top_k : int
            Number of results to return.

        Returns
        -------
        List[SearchResult]
        """
        self.statistics["queries"] += 1

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        search_results: List[SearchResult] = []

        for i in range(len(results["ids"][0])):
            search_results.append(
                SearchResult(
                    chunk_id=results["ids"][0][i],
                    score=1.0 - results["distances"][0][i],
                    text=results["documents"][0][i],
                    metadata=results["metadatas"][0][i],
                )
            )

        return search_results

    # ==========================================================
    # Statistics
    # ==========================================================

    def reset_statistics(self) -> None:
        """
        Reset runtime statistics.
        """

        self.statistics = {

            "indexed_vectors": 0,

            "documents": 0,

            "batches": 0,

            "queries": 0,

            "duplicates": 0,

            "collection_size": self.collection.count(),

        }

        logger.info(
            "Indexer statistics reset."
        )

    # ==========================================================
    # Summary
    # ==========================================================

    def print_summary(self) -> None:
        """
        Print index summary.
        """

        stats = self.get_statistics()

        logger.info(
            "========== VECTOR STORE SUMMARY =========="
        )

        logger.info(
            "Collection : %s",
            self.collection_name,
        )

        logger.info(
            "Vectors : %d",
            stats["collection_size"],
        )

        logger.info(
            "Indexed Vectors : %d",
            stats["indexed_vectors"],
        )

        logger.info(
            "Documents : %d",
            stats["documents"],
        )

        logger.info(
            "Batches : %d",
            stats["batches"],
        )

        logger.info(
            "Queries : %d",
            stats["queries"],
        )

        logger.info(
            "Duplicates : %d",
            stats["duplicates"],
        )

        logger.info(
            "Persistence : %s",
            self.persist_directory,
        )

        logger.info(
            "=========================================="
        )

    # ==========================================================
    # Magic Methods
    # ==========================================================

    def __len__(self) -> int:
        """
        Number of vectors in the collection.
        """

        return self.collection.count()

    def __contains__(
        self,
        chunk_id: str,
    ) -> bool:
        """
        Check if a chunk exists.
        """

        return chunk_id in self._existing_ids()

    def __repr__(self) -> str:
        """
        Developer-friendly representation.
        """

        return (

            "VectorIndexer("

            f"collection='{self.collection_name}', "

            f"vectors={self.collection.count()}, "

            f"batch_size={self.batch_size}"

            ")"

        )