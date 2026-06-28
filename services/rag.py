"""
Enterprise Knowledge Assistant
RAG Pipeline
"""

from __future__ import annotations

import logging
import os
import time

from dataclasses import dataclass, field
from typing import Any

from groq import Groq

from dotenv import load_dotenv

from retrieval.retrieval import EnterpriseRetriever
from retrieval.models import RetrievalResponse, RetrievedChunk
from langchain_core.documents import Document
from services.prompts import build_prompt as build_prompt_template


load_dotenv()

logger = logging.getLogger(__name__)

@dataclass
class RAGResponse:
    """
    Standard response returned by the RAG pipeline.
    """
    question: str
    answer: str
    sources: list[dict[str, Any]] = field(default_factory=list)
    retrieved_documents: int = 0
    latency: float = 0.0


@dataclass
class RAGStatistics:
    """
    Runtime statistics.
    """
    total_queries: int = 0
    successful_queries: int = 0
    failed_queries: int = 0
    total_latency: float = 0.0
    retrieval_latency: float = 0.0
    generation_latency: float = 0.0

class RAGService:
    """
    Enterprise Retrieval-Augmented Generation service.
    """

    def __init__(
        self,
        model_name: str = "llama-3.3-70b-versatile",
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ):

        logger.info("Initializing RAG service...")

        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found in environment variables."
            )

        self.client = Groq(
            api_key=api_key,
        )

        self.retriever = EnterpriseRetriever()
        self.statistics = RAGStatistics()

        logger.info("RAG service initialized.")
        logger.info("Model : %s", self.model_name)

    def _format_context(
        self,
        documents,
    ) -> str:
        """
        Convert retrieved documents into prompt context.
        """
        # Accept either a RetrievalResponse or an iterable of RetrievedChunk
        chunks = []

        if isinstance(documents, RetrievalResponse):
            chunks = documents.retrieved_chunks
        else:
            chunks = list(documents or [])

        sections = []

        for index, chunk in enumerate(chunks, start=1):

            metadata = getattr(chunk, "metadata", {}) or {}

            section = (
                f"[Document {index}]\n"
                f"Source: {getattr(chunk, 'document', metadata.get('document'))}\n"
                f"Page: {getattr(chunk, 'page', metadata.get('page'))}\n\n"
                f"{getattr(chunk, 'text', '')}"
            )

            sections.append(section)

        return "\n\n".join(sections)

    def _build_prompt(
        self,
        question: str,
        documents,
    ) -> str:
        """
        Build the final prompt for the LLM.
        """

        # Convert retrieved chunks (or a RetrievalResponse) into
        # langchain `Document` objects expected by the prompt builder.
        chunks = (
            documents.retrieved_chunks
            if isinstance(documents, RetrievalResponse)
            else list(documents or [])
        )

        docs = [
            Document(page_content=chunk.text, metadata=chunk.metadata)
            for chunk in chunks
        ]

        return build_prompt_template(
            question=question,
            documents=docs,
        )

    def reset_statistics(self) -> None:
        """
        Reset runtime statistics.
        """
        self.statistics = RAGStatistics()
        logger.info("RAG statistics reset.")

    def retrieve(
        self,
        question: str,
    ):
        """
        Retrieve relevant documents for a question.
        """

        logger.info("Question: %s", question)
        logger.info("Running document retrieval...")

        # The retriever returns a RetrievalResponse containing RetrievedChunk items
        response = self.retriever.retrieve(question)

        # Keep retrieval latency in statistics (ms)
        try:
            self.statistics.retrieval_latency = response.latency_ms
        except Exception:
            self.statistics.retrieval_latency = 0.0

        logger.info(
            "Retrieved %d chunk(s) in %.2f ms.",
            response.result_count,
            response.latency_ms,
        )

        return response

    @staticmethod
    def has_context(
        documents,
    ) -> bool:
        """
        Returns True if retrieval returned documents.
        """

        if isinstance(documents, RetrievalResponse):
            return documents.result_count > 0

        try:
            return len(documents) > 0
        except Exception:
            return False

    @staticmethod
    def extract_sources(
        documents,
    ) -> list[dict]:
        """
        Extract document metadata.
        """

        # Accept either a RetrievalResponse or iterable of RetrievedChunk
        chunks = (
            documents.retrieved_chunks
            if isinstance(documents, RetrievalResponse)
            else list(documents or [])
        )

        sources = []
        seen = set()

        for chunk in chunks:

            source = {
                "document": getattr(chunk, "document", None) or chunk.metadata.get("document"),
                "page": getattr(chunk, "page", None) or chunk.metadata.get("page"),
                "category": getattr(chunk, "category", None) or chunk.metadata.get("category"),
            }

            key = (source["document"], source["page"])

            if key not in seen:
                seen.add(key)
                sources.append(source)

        return sources

    def retrieval_summary(
        self,
        documents,
    ) -> None:
        """
        Log retrieval summary.
        """

        logger.info("=" * 50)
        logger.info("RETRIEVAL SUMMARY")
        logger.info("=" * 50)

        # Accept RetrievalResponse or iterable of chunks
        if isinstance(documents, RetrievalResponse):
            count = documents.result_count
            chunks = documents.retrieved_chunks
        else:
            chunks = list(documents or [])
            count = len(chunks)

        logger.info(
            "Documents Retrieved : %d",
            count,
        )

        logger.info(
            "Latency : %.2f ms",
            self.statistics.retrieval_latency,
        )

        for index, chunk in enumerate(chunks, start=1):

            logger.info(
                "%d. %s (Page %s)",
                index,
                getattr(chunk, "document", chunk.metadata.get("document")),
                getattr(chunk, "page", chunk.metadata.get("page")),
            )

        logger.info("=" * 50)

    def test_retrieval(
        self,
        question: str,
    ):
        """
        Test retrieval only.
        """

        documents = self.retrieve(question)

        self.retrieval_summary(documents)

        return documents

    # ==========================================================
    # LLM Generation
    # ==========================================================

    def _generate_answer(
        self,
        prompt: str,
    ) -> str:
        """
        Generate an answer from the LLM.
        """
        logger.info("Generating answer using Groq...")
        start = time.perf_counter()

        response = self.client.chat.completions.create(
            model=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an Enterprise Knowledge Assistant."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        generation_time = (
            time.perf_counter() - start
        ) * 1000

        self.statistics.generation_latency = (
            generation_time
        )

        logger.info(
            "Generation completed in %.2f ms.",
            generation_time,
        )

        return self._parse_response(response)

    # ==========================================================
    # Response Parser
    # ==========================================================

    @staticmethod
    def _parse_response(
        response,
    ) -> str:
        """
        Extract assistant response text.
        """
        try:
            return (
                response
                .choices[0]
                .message
                .content
                .strip()
            )

        except Exception as exc:
            logger.exception(
                "Failed to parse LLM response: %s",
                exc,
            )

            raise RuntimeError(
                "Invalid LLM response."
            )

    # ==========================================================
    # Prompt Construction
    # ==========================================================

    def build_prompt(
        self,
        question: str,
        documents,
    ) -> str:
        """
        Build the final RAG prompt.
        """
        logger.info(
            "Building prompt..."
        )
        prompt = self._build_prompt(
            question=question,
            documents=documents,
        )

        logger.info(
            "Prompt size : %d characters",
            len(prompt),
        )

        return prompt

    # ==========================================================
    # Generation Test
    # ==========================================================

    def test_generation(
        self,
        question: str,
    ) -> str:
        """
        Test retrieval and generation.
        """

        documents = self.retrieve(question)

        if not self.has_context(
            documents
        ):

            logger.warning(
                "No context retrieved."
            )

            return (
                "I could not find this information "
                "in the provided knowledge base."
            )

        prompt = self.build_prompt(

            question,

            documents,

        )

        answer = self._generate_answer(
            prompt
        )

        logger.info(
            "Answer generated successfully."
        )

        return answer
    

    # ==========================================================
    # RAG Pipeline
    # ==========================================================

    def answer_question(
        self,
        question: str,
    ) -> RAGResponse:
        """
        Complete RAG pipeline.

        Question
            ↓
        Retriever
            ↓
        Prompt
            ↓
        Groq
            ↓
        Answer
            ↓
        Sources
        """

        logger.info("=" * 70)
        logger.info("NEW QUESTION")
        logger.info("=" * 70)
        logger.info(question)

        overall_start = time.perf_counter()

        self.statistics.total_queries += 1

        try:
            # -----------------------------------------
            # Retrieve
            # -----------------------------------------
            documents = self.retrieve(question)

            if not self.has_context(documents):

                logger.warning(
                    "No documents retrieved."
                )

                return self._empty_response(
                    question
                )

            # -----------------------------------------
            # Prompt
            # -----------------------------------------

            prompt = self.build_prompt(
                question,
                documents,
            )

            # -----------------------------------------
            # Generate
            # -----------------------------------------

            answer = self._generate_answer(
                prompt
            )

            # -----------------------------------------
            # Sources
            # -----------------------------------------

            sources = self.extract_sources(
                documents
            )

            latency = (
                time.perf_counter()
                - overall_start
            ) * 1000

            self.statistics.successful_queries += 1

            self.statistics.total_latency += (
                latency
            )

            logger.info(
                "Pipeline completed in %.2f ms",
                latency,
            )

            return RAGResponse(
                question=question,
                answer=answer,
                sources=sources,
                retrieved_documents=(
                    documents.result_count
                    if isinstance(documents, RetrievalResponse)
                    else len(documents)
                ),
                latency=latency,
            )

        except Exception:
            self.statistics.failed_queries += 1
            logger.exception(
                "Pipeline failed."
            )

            raise

    # ==========================================================
    # Empty Response
    # ==========================================================

    @staticmethod
    def _empty_response(
        question: str,
    ) -> RAGResponse:
        """
        Return assignment-required fallback.
        """
        return RAGResponse(
            question=question,
            answer=(
                "I could not find this information "
                "in the provided knowledge base."
            ),
            sources=[],
            retrieved_documents=0,
            latency=0.0,

        )
    
    # ==========================================================
    # Response Printer
    # ==========================================================

    @staticmethod
    def print_response(
        response: RAGResponse,
    ) -> None:
        """
        Pretty-print a response.
        """

        print()

        print("=" * 80)

        print("QUESTION")

        print("=" * 80)

        print(response.question)

        print()

        print("=" * 80)

        print("ANSWER")

        print("=" * 80)

        print(response.answer)

        print()

        print("=" * 80)

        print("SOURCES")

        print("=" * 80)

        if response.sources:

            for source in response.sources:

                print(
                    f"{source['document']} "
                    f"(Page {source['page']})"
                )

        else:
            print("No sources.")

        print()

        print("=" * 80)

        print(
            f"Retrieved Documents : "
            f"{response.retrieved_documents}"
        )

        print(
            f"Latency : "
            f"{response.latency:.2f} ms"
        )

        print("=" * 80)

    # ==========================================================
    # Statistics
    # ==========================================================

    def statistics_dict(
        self,
    ) -> dict[str, Any]:
        """
        Export statistics.
        """

        average_latency = 0.0

        if self.statistics.successful_queries:
            average_latency = (self.statistics.total_latency / self.statistics.successful_queries)

        return {
            "queries":
                self.statistics.total_queries,

            "successful":
                self.statistics.successful_queries,

            "failed":
                self.statistics.failed_queries,

            "average_latency_ms":
                round(
                    average_latency,
                    2,
                ),

            "retrieval_latency_ms":
                round(
                    self.statistics.retrieval_latency,
                    2,
                ),

            "generation_latency_ms":
                round(
                    self.statistics.generation_latency,
                    2,
                ),
        }

    def print_statistics(
        self,
    ) -> None:
        """
        Print runtime statistics.
        """

        stats = self.statistics_dict()

        logger.info("=" * 60)

        logger.info("RAG PIPELINE SUMMARY")

        logger.info("=" * 60)

        for key, value in stats.items():

            logger.info(
                "%-24s : %s",
                key,
                value,
            )

        logger.info("=" * 60)

    # ==========================================================
    # Health Check
    # ==========================================================

    def health_check(self) -> bool:
        """
        Verify that the RAG pipeline is ready.
        """

        try:
            if self.client is None:
                return False

            if self.retriever is None:
                return False

            return True

        except Exception:
            return False

    # ==========================================================
    # Service Information
    # ==========================================================

    def info(self) -> dict[str, Any]:
        """
        Return configuration information.
        """

        return {
            "model": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "retriever_top_k": 5,
            "health": self.health_check(),
        }

    # ==========================================================
    # Runtime Summary
    # ==========================================================

    def print_summary(self) -> None:
        """
        Print service configuration and runtime statistics.
        """

        logger.info("=" * 70)
        logger.info("RAG SERVICE SUMMARY")
        logger.info("=" * 70)

        info = self.info()

        logger.info(
            "Model               : %s",
            info["model"],
        )

        logger.info(
            "Temperature         : %.2f",
            info["temperature"],
        )

        logger.info(
            "Maximum Tokens      : %d",
            info["max_tokens"],
        )

        logger.info(
            "Retriever Top-K     : %d",
            info["retriever_top_k"],
        )

        logger.info(
            "Healthy             : %s",
            info["health"],
        )

        logger.info("")

        self.print_statistics()

    # ==========================================================
    # Magic Methods
    # ==========================================================

    def __repr__(self) -> str:
        """
        Developer representation.
        """
        return (
            f"{self.__class__.__name__}("
            f"model='{self.model_name}', "
            f"temperature={self.temperature}, "
            f"max_tokens={self.max_tokens})"
        )

    def __str__(self) -> str:
        """
        Human-readable representation.
        """

        return (

            f"Enterprise Knowledge Assistant "

            f"({self.model_name})"

        )

__all__ = [
    "RAGService",
    "RAGResponse",
    "RAGStatistics",
]