"""
Enterprise Knowledge Assistant
Application Configuration

Loads environment variables from .env using Pydantic Settings.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central application settings.
    """

    # --------------------------------------------------------
    # Application
    # --------------------------------------------------------

    APP_NAME: str = "Enterprise Knowledge Assistant"
    APP_ENV: str = "development"

    # --------------------------------------------------------
    # Groq LLM
    # --------------------------------------------------------

    GROQ_API_KEY: str = Field(default="")
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # --------------------------------------------------------
    # Local Embeddings (BGE)
    # --------------------------------------------------------

    EMBEDDING_MODEL: str = "BAAI/bge-base-en-v1.5"

    # --------------------------------------------------------
    # Paths
    # --------------------------------------------------------

    RAW_DATA_PATH: Path = Path("data/raw")
    VECTOR_DB_PATH: Path = Path("data/vectorstore")
    LOG_DIRECTORY: Path = Path("logs")

    # --------------------------------------------------------
    # Retrieval
    # --------------------------------------------------------

    TOP_K: int = 5

    # --------------------------------------------------------
    # Chunking
    # --------------------------------------------------------

    CHUNK_SIZE: int = 900
    CHUNK_OVERLAP: int = 150

    # --------------------------------------------------------
    # Embeddings
    # --------------------------------------------------------

    EMBEDDING_BATCH_SIZE: int = 32
    VECTOR_DIMENSION: int = 768
    ENABLE_BATCHING: bool = True

    # --------------------------------------------------------
    # Logging
    # --------------------------------------------------------

    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # --------------------------------------------------------
    # LLM Settings
    # --------------------------------------------------------

    LLM_MAX_TOKENS: int = 4096
    LLM_TEMPERATURE: float = 0.0


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached Settings object.
    """
    return Settings()


settings = get_settings()
