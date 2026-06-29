"""
Enterprise Knowledge Assistant
API Schemas

Defines request and response models used by the FastAPI backend.
"""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, ConfigDict, Field


# =====================================================================
# Request Models
# =====================================================================


class QuestionRequest(BaseModel):
    """
    Incoming question from the client.
    """

    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Natural language question.",
        examples=[
            "What is the password policy?",
        ],
    )

    session_id: str | None = Field(
        default=None,
        description="Optional conversation session identifier for follow-up questions.",
        examples=[
            "optional-session-id",
        ],
    )

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "question": "What is the password policy?",
                "session_id": "optional-session-id",
            }
        },
    )


# =====================================================================
# Source Models
# =====================================================================


class SourceResponse(BaseModel):
    """
    Single source citation returned with the answer.
    """

    document: str = Field(
        ...,
        description="Document name.",
    )

    page: int = Field(
        ...,
        ge=1,
        description="Page number.",
    )

    category: str = Field(
        ...,
        description="Document category.",
    )

    chunk_id: str = Field(
        ...,
        description="Unique chunk identifier.",
    )


# =====================================================================
# Question Response
# =====================================================================


class QuestionResponse(BaseModel):
    """
    Response returned by POST /ask.
    """

    answer: str

    sources: List[SourceResponse]

    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score.",
    )

    latency: float = Field(
        ...,
        ge=0.0,
        description="Pipeline latency in seconds.",
    )

    retrieved_documents: int = Field(
        ...,
        ge=0,
        description="Number of retrieved chunks.",
    )


# =====================================================================
# Health Response
# =====================================================================


class HealthResponse(BaseModel):
    """
    Returned by GET /health.
    """

    status: str

    application: str

    version: str

    llm_model: str

    embedding_model: str

    vector_database: str

    collection_name: str


# =====================================================================
# Error Response
# =====================================================================


class ErrorResponse(BaseModel):
    """
    Standard API error response.
    """

    detail: str


# =====================================================================
# Public Exports
# =====================================================================


__all__ = [
    "QuestionRequest",
    "QuestionResponse",
    "SourceResponse",
    "HealthResponse",
    "ErrorResponse",
]