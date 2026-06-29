"""
Enterprise Knowledge Assistant
API Routes

Defines all REST endpoints.

Endpoints
---------
GET     /
GET     /health
POST    /ask
"""

from __future__ import annotations

import time

from fastapi import APIRouter, HTTPException, status

from app.core.config import settings
from app.core.logger import get_logger
from app.schemas.api import (
    ErrorResponse,
    HealthResponse,
    QuestionRequest,
    QuestionResponse,
    SourceResponse,
)
from services.rag import RAGService


logger = get_logger(__name__)

router = APIRouter()

# ---------------------------------------------------------------------
# Global RAG Service
# ---------------------------------------------------------------------

rag_service = RAGService()


# ---------------------------------------------------------------------
# Root Endpoint
# ---------------------------------------------------------------------


@router.get(
    "/",
    tags=["General"],
)
async def root():
    """
    Root endpoint.
    """

    return {
        "application": settings.APP_NAME,
        "status": "running",
        "docs": "/docs",
    }


# ---------------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------------


@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
)
async def health_check():
    """
    Health check endpoint.
    """

    return HealthResponse(
        status="healthy",
        application=settings.APP_NAME,
        version="1.0.0",
        llm_model=settings.GROQ_MODEL,
        embedding_model=settings.EMBEDDING_MODEL,
        vector_database="ChromaDB",
        collection_name=settings.VECTOR_COLLECTION_NAME,
    )


# ---------------------------------------------------------------------
# Ask Endpoint
# ---------------------------------------------------------------------


@router.post(
    "/ask",
    response_model=QuestionResponse,
    responses={
        500: {
            "model": ErrorResponse,
        }
    },
    tags=["RAG"],
)
async def ask_question(
    request: QuestionRequest,
):
    """
    Enterprise RAG endpoint.
    """

    logger.info(
        "Received question: %s",
        request.question,
    )

    start = time.perf_counter()

    try:
        result = rag_service.answer_question(
            request.question,
            session_id=request.session_id or "default",
        )

    except Exception as exc:
        logger.exception(
            "RAG pipeline failed: %s",
            exc,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )

    elapsed = round(time.perf_counter() - start, 3)

    sources = []

    for source in result.sources:
        sources.append(
            SourceResponse(
                document=source.get("document", "Unknown"),
                page=source.get("page", 0),
                category=source.get("category", "unknown"),
                chunk_id=source.get("chunk_id", ""),
            )
        )

    logger.info(
        "Question answered in %.3f seconds.",
        elapsed,
    )

    return QuestionResponse(
        answer=result.answer,
        sources=sources,
        confidence=result.confidence,
        latency=elapsed,
        retrieved_documents=result.retrieved_documents
    )
