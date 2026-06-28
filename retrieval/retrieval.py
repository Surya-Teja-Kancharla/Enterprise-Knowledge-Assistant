"""
Enterprise Knowledge Assistant
Retriever

Responsibilities
----------------
- Load ChromaDB
- Load embedding model
- Configure retrieval
- Perform MMR search
- Return retrieved chunks

This module intentionally DOES NOT:
- Generate LLM responses
- Build prompts
- Maintain conversation history
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import chromadb
from chromadb import PersistentClient
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.core.logger import get_logger
from retrieval.models import (
    RetrievedChunk,
    RetrievalResponse,
)

from retrieval.filters import (
    category_filter,
    document_filter,
    page_filter,
)

logger = get_logger(__name__)


class EnterpriseRetriever:
    """
    Production-ready semantic retriever.

    Supports:

    - ChromaDB persistence
    - Local BGE embeddings
    - MMR retrieval
    - Metadata filtering
    """

    def __init__(
        self,
        persist_directory: str | Path = settings.VECTOR_DB_PATH,
        collection_name: str = settings.VECTOR_COLLECTION_NAME,
    ) -> None:

        self.persist_directory = Path(persist_directory)

        self.collection_name = collection_name

        logger.info("Initializing Retriever...")

        self.client = self._initialize_client()

        self.collection = self._load_collection()

        self.embedding_model = self._load_embedding_model()

        self.statistics = {
            "queries": 0,
            "retrieved_chunks": 0,
            "average_latency_ms": 0.0,
            "last_query": "",
        }

        logger.info("Retriever initialized successfully.")

        logger.info(
            "Collection : %s",
            self.collection_name,
        )

        logger.info(
            "Persistence : %s",
            self.persist_directory,
        )

        logger.info(
            "Embedding Model : %s",
            settings.EMBEDDING_MODEL,
        )

        # --------------------------------------------------------
    # Initialization
    # --------------------------------------------------------

    def _initialize_client(
        self,
    ) -> PersistentClient:
        """
        Initialize persistent ChromaDB client.
        """

        logger.info(
            "Loading ChromaDB..."
        )

        return chromadb.PersistentClient(
            path=str(self.persist_directory)
        )


    def _load_collection(self):
        """
        Load existing collection.
        """

        logger.info(
            "Opening collection..."
        )

        try:

            collection = self.client.get_collection(
                self.collection_name
            )

        except Exception as exc:

            logger.exception(
                "Collection '%s' not found.",
                self.collection_name,
            )

            raise RuntimeError(
                "Vector database has not been indexed yet."
            ) from exc

        logger.info(
            "Collection loaded successfully."
        )

        return collection


    def _load_embedding_model(
        self,
    ) -> SentenceTransformer:
        """
        Load the embedding model once.

        The same model used during indexing
        must also be used for querying.
        """

        logger.info(
            "Loading embedding model..."
        )

        model = SentenceTransformer(
            settings.EMBEDDING_MODEL
        )

        logger.info(
            "Embedding model loaded."
        )

        return model

        # --------------------------------------------------------
    # Utilities
    # --------------------------------------------------------

    @property
    def vector_count(
        self,
    ) -> int:
        """
        Returns number of indexed vectors.
        """

        return self.collection.count()

    # --------------------------------------------------------
    # Query Embedding
    # --------------------------------------------------------

    def embed_query(
        self,
        query: str,
    ) -> list[float]:
        """
        Generate an embedding for a user query.

        Parameters
        ----------
        query : str
            Natural language search query.

        Returns
        -------
        list[float]
            Normalized embedding vector.
        """

        query = query.strip()

        if not query:
            raise ValueError(
                "Query cannot be empty."
            )

        logger.info(
            "Generating query embedding..."
        )

        embedding = self.embedding_model.encode(
            query,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

        return embedding.tolist()

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    @staticmethod
    def _validate_query(
        query: str,
    ) -> None:
        """
        Validate user query.
        """

        if not isinstance(query, str):
            raise TypeError(
                "Query must be a string."
            )

        if not query.strip():
            raise ValueError(
                "Query cannot be empty."
            )

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    def _update_statistics(
        self,
        query: str,
        latency_ms: float,
        retrieved_chunks: int,
    ) -> None:
        """
        Update retrieval statistics.
        """

        self.statistics["queries"] += 1

        self.statistics["retrieved_chunks"] += (
            retrieved_chunks
        )

        self.statistics["last_query"] = query

        total_queries = self.statistics["queries"]

        previous_average = self.statistics[
            "average_latency_ms"
        ]

        self.statistics["average_latency_ms"] = round(
            (
                (previous_average * (total_queries - 1))
                + latency_ms
            )
            / total_queries,
            2,
        )

    # --------------------------------------------------------
    # Public Utilities
    # --------------------------------------------------------

    def get_statistics(
        self,
    ) -> dict[str, Any]:
        """
        Return retrieval statistics.
        """

        return dict(
            self.statistics
        )

    def reset_statistics(
        self,
    ) -> None:
        """
        Reset runtime statistics.
        """

        self.statistics = {
            "queries": 0,
            "retrieved_chunks": 0,
            "average_latency_ms": 0.0,
            "last_query": "",
        }

        logger.info(
            "Retriever statistics reset."
        )

    # --------------------------------------------------------
    # LangChain Retriever
    # --------------------------------------------------------

    def _build_retriever(self):
        """
        Build a LangChain MMR retriever.

        MMR returns diverse chunks instead of
        multiple nearly-identical chunks.
        """

        embedding_function = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL,
            encode_kwargs={
                "normalize_embeddings": True,
            },
        )

        vectorstore = Chroma(
            persist_directory=str(
                self.persist_directory
            ),
            collection_name=self.collection_name,
            embedding_function=embedding_function,
        )

        retriever = vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": settings.TOP_K,
                "fetch_k": 20,
                "lambda_mult": 0.5,
            },
        )

        return retriever

    # --------------------------------------------------------
    # MMR Retrieval
    # --------------------------------------------------------

    def retrieve(
        self,
        query: str,
    ) -> RetrievalResponse:
        """
        Retrieve the most relevant chunks
        using Maximal Marginal Relevance (MMR).
        """

        self._validate_query(query)

        logger.info(
            "Running MMR retrieval..."
        )

        start_time = time.perf_counter()

        retriever = self._build_retriever()

        documents = retriever.invoke(
            query
        )

        latency_ms = (
            time.perf_counter()
            - start_time
        ) * 1000

        response = RetrievalResponse(
            query=query,
            search_type="mmr",
            top_k=settings.TOP_K,
            latency_ms=round(
                latency_ms,
                2,
            ),
            total_candidates=len(
                documents
            ),
        )

        for index, document in enumerate(
            documents,
            start=1,
        ):

            metadata = dict(
                document.metadata
            )

            response.add_chunk(
                RetrievedChunk(
                    chunk_id=metadata.get(
                        "chunk_id",
                        "",
                    ),
                    text=document.page_content,
                    score=1.0,
                    metadata=metadata,
                    document=metadata.get(
                        "document",
                        "",
                    ),
                    page=metadata.get(
                        "page",
                        0,
                    ),
                    category=metadata.get(
                        "category",
                        "",
                    ),
                    source=metadata.get(
                        "source",
                        "",
                    ),
                    chunk_number=metadata.get(
                        "chunk_number",
                        index,
                    ),
                )
            )

        response.calculate_average_score()

        self._update_statistics(
            query,
            response.latency_ms,
            response.result_count,
        )

        logger.info(
            "Retrieved %d chunks in %.2f ms.",
            response.result_count,
            response.latency_ms,
        )

        return response

    # --------------------------------------------------------
    # Filtered Retrieval
    # --------------------------------------------------------

    def retrieve_with_filter(
        self,
        query: str,
        metadata_filter: dict[str, Any],
    ) -> RetrievalResponse:
        """
        Retrieve chunks using metadata filters.

        Parameters
        ----------
        query : str

        metadata_filter : dict

        Example
        -------
        {
            "category": "hr"
        }
        """

        self._validate_query(query)

        logger.info(
            "Running filtered retrieval..."
        )

        start_time = time.perf_counter()

        embedding_function = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL,
            encode_kwargs={
                "normalize_embeddings": True,
            },
        )

        vectorstore = Chroma(
            persist_directory=str(
                self.persist_directory
            ),
            collection_name=self.collection_name,
            embedding_function=embedding_function,
        )

        retriever = vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": settings.TOP_K,
                "fetch_k": 20,
                "lambda_mult": 0.5,
                "filter": metadata_filter,
            },
        )

        documents = retriever.invoke(
            query
        )

        latency_ms = (
            time.perf_counter()
            - start_time
        ) * 1000

        response = RetrievalResponse(
            query=query,
            search_type="mmr",
            top_k=settings.TOP_K,
            latency_ms=round(
                latency_ms,
                2,
            ),
            total_candidates=len(
                documents
            ),
        )

        for index, document in enumerate(
            documents,
            start=1,
        ):

            metadata = dict(
                document.metadata
            )

            response.add_chunk(
                RetrievedChunk(
                    chunk_id=metadata.get(
                        "chunk_id",
                        "",
                    ),
                    text=document.page_content,
                    score=1.0,
                    metadata=metadata,
                    document=metadata.get(
                        "document",
                        "",
                    ),
                    page=metadata.get(
                        "page",
                        0,
                    ),
                    category=metadata.get(
                        "category",
                        "",
                    ),
                    source=metadata.get(
                        "source",
                        "",
                    ),
                    chunk_number=metadata.get(
                        "chunk_number",
                        index,
                    ),
                )
            )

        response.calculate_average_score()

        self._update_statistics(
            query,
            response.latency_ms,
            response.result_count,
        )

        return response

    # --------------------------------------------------------
    # Category Search
    # --------------------------------------------------------

    def retrieve_category(
        self,
        query: str,
        category: str,
    ) -> RetrievalResponse:
        """
        Retrieve only from one category.
        """

        return self.retrieve_with_filter(
            query,
            category_filter(category),
        )

    # --------------------------------------------------------
    # Document Search
    # --------------------------------------------------------

    def retrieve_document(
        self,
        query: str,
        document: str,
    ) -> RetrievalResponse:
        """
        Retrieve only from one document.
        """

        return self.retrieve_with_filter(
            query,
            document_filter(document),
        )

    # --------------------------------------------------------
    # Page Search
    # --------------------------------------------------------

    def retrieve_page(
        self,
        query: str,
        document: str,
        page: int,
    ) -> RetrievalResponse:
        """
        Retrieve only from one page.
        """

        return self.retrieve_with_filter(
            query,
            page_filter(document, page),
        )

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    def export_statistics(
        self,
    ) -> dict[str, Any]:
        """
        Export retriever statistics.
        """

        return {
            "collection": self.collection_name,
            "vector_count": self.vector_count,
            "queries": self.statistics["queries"],
            "retrieved_chunks":
                self.statistics["retrieved_chunks"],
            "average_latency_ms":
                self.statistics["average_latency_ms"],
            "last_query":
                self.statistics["last_query"],
            "embedding_model":
                settings.EMBEDDING_MODEL,
            "search_type": "mmr",
            "top_k": settings.TOP_K,
        }

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    def print_summary(
        self,
    ) -> None:
        """
        Print retriever summary.
        """

        stats = self.export_statistics()

        logger.info(
            "========== RETRIEVAL SUMMARY =========="
        )

        logger.info(
            "Collection : %s",
            stats["collection"],
        )

        logger.info(
            "Vectors : %d",
            stats["vector_count"],
        )

        logger.info(
            "Search Type : %s",
            stats["search_type"],
        )

        logger.info(
            "Top K : %d",
            stats["top_k"],
        )

        logger.info(
            "Queries : %d",
            stats["queries"],
        )

        logger.info(
            "Retrieved Chunks : %d",
            stats["retrieved_chunks"],
        )

        logger.info(
            "Average Latency : %.2f ms",
            stats["average_latency_ms"],
        )

        logger.info(
            "Last Query : %s",
            stats["last_query"],
        )

        logger.info(
            "Embedding Model : %s",
            stats["embedding_model"],
        )

        logger.info(
            "======================================="
        )

    # --------------------------------------------------------
    # Health Check
    # --------------------------------------------------------

    def health_check(
        self,
    ) -> bool:
        """
        Verify retriever health.
        """

        try:

            if self.collection.count() <= 0:

                logger.warning(
                    "Collection is empty."
                )

                return False

            if self.embedding_model is None:

                logger.warning(
                    "Embedding model not loaded."
                )

                return False

            logger.info(
                "Retriever health check passed."
            )

            return True

        except Exception as exc:

            logger.exception(
                "Retriever health check failed: %s",
                exc,
            )

            return False

    # --------------------------------------------------------
    # Convenience Properties
    # --------------------------------------------------------

    @property
    def total_queries(
        self,
    ) -> int:
        """
        Total queries executed.
        """

        return self.statistics["queries"]

    @property
    def average_latency(
        self,
    ) -> float:
        """
        Average retrieval latency.
        """

        return self.statistics[
            "average_latency_ms"
        ]

    @property
    def total_retrieved_chunks(
        self,
    ) -> int:
        """
        Total retrieved chunks.
        """

        return self.statistics[
            "retrieved_chunks"
        ]

    # --------------------------------------------------------
    # Magic Methods
    # --------------------------------------------------------

    def __len__(
        self,
    ) -> int:
        """
        Number of indexed vectors.
        """

        return self.vector_count

    def __repr__(
        self,
    ) -> str:
        """
        Developer-friendly representation.
        """

        return (
            "EnterpriseRetriever("
            f"collection='{self.collection_name}', "
            f"vectors={self.vector_count}, "
            f"search_type='mmr', "
            f"top_k={settings.TOP_K}"
            ")"
        )
