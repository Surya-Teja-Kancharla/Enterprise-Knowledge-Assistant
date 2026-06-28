"""
Enterprise Knowledge Assistant

Application Configuration

Centralized application settings loaded from the .env file
using Pydantic Settings.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    """
    Central application settings.
    """

    # ==========================================================
    # Application
    # ==========================================================

    APP_NAME: str = "Enterprise Knowledge Assistant"

    APP_ENV: str = "development"

    VERSION: str = "1.0.0"

    # ==========================================================
    # Groq
    # ==========================================================

    GROQ_API_KEY: str = Field(default="")

    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    LLM_TEMPERATURE: float = 0.0

    LLM_MAX_TOKENS: int = 4096

    # ==========================================================
    # Embeddings
    # ==========================================================

    EMBEDDING_MODEL: str = (
        "BAAI/bge-base-en-v1.5"
    )

    VECTOR_DIMENSION: int = 768

    EMBEDDING_BATCH_SIZE: int = 32

    ENABLE_BATCHING: bool = True

    # ==========================================================
    # Chunking
    # ==========================================================

    CHUNK_SIZE: int = 900

    CHUNK_OVERLAP: int = 150

    # ==========================================================
    # Retrieval
    # ==========================================================

    TOP_K: int = 5

    RETRIEVAL_TOP_K: int = 5

    ENABLE_RERANKING: bool = False

    SIMILARITY_THRESHOLD: float = 0.25

    # ==========================================================
    # Vector Store
    # ==========================================================

    VECTOR_DB_PATH: Path = Path(
        "data/vectorstore"
    )

    VECTOR_COLLECTION_NAME: str = (
        "enterprise_knowledge"
    )

    VECTOR_DISTANCE: str = "cosine"

    INDEX_BATCH_SIZE: int = 100

    # ==========================================================
    # Paths
    # ==========================================================

    RAW_DATA_PATH: Path = Path(
        "data/raw"
    )

    PROCESSED_DATA_PATH: Path = Path(
        "data/processed"
    )

    LOG_DIRECTORY: Path = Path(
        "logs"
    )

    # ==========================================================
    # FastAPI
    # ==========================================================

    API_HOST: str = "0.0.0.0"

    API_PORT: int = 8000

    API_TITLE: str = (
        "Enterprise Knowledge Assistant API"
    )

    # ==========================================================
    # Streamlit
    # ==========================================================

    STREAMLIT_PORT: int = 8501

    # ==========================================================
    # Logging
    # ==========================================================

    LOG_LEVEL: str = "INFO"

    # ==========================================================
    # Evaluation
    # ==========================================================

    SAVE_RETRIEVAL_LOGS: bool = True

    SAVE_CHAT_HISTORY: bool = False

    # ==========================================================
    # Pydantic Configuration
    # ==========================================================

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Return cached application settings.
    """
    return Settings()

settings = get_settings()
