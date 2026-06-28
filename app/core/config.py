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

    APP_NAME: str = "Enterprise Knowledge Assistant"

    OPENAI_API_KEY: str = Field(default="")

    OPENAI_MODEL: str = "gpt-4.1"

    EMBEDDING_MODEL: str = "text-embedding-3-large"

    RAW_DATA_PATH: Path = Path("data/raw")

    VECTOR_DB_PATH: Path = Path("data/vectorstore")

    LOG_DIRECTORY: Path = Path("logs")

    TOP_K: int = 5

    CHUNK_SIZE: int = 800

    CHUNK_OVERLAP: int = 150

    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached Settings object.
    """
    return Settings()


settings = get_settings()