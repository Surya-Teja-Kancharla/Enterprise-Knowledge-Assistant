"""
Enterprise Knowledge Assistant
Pytest Fixtures

Shared fixtures for all unit tests.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from ingestion.parsers.loader import PDFLoader
from ingestion.chunking.chunker import DocumentChunker
from retrieval.retrieval import EnterpriseRetriever
from app.api.main import app


DOCUMENTS_DIR = Path("data/raw")


@pytest.fixture(scope="session")
def loader() -> PDFLoader:
    """
    Shared PDF loader.
    """
    return PDFLoader(DOCUMENTS_DIR)


@pytest.fixture(scope="session")
def documents(loader):
    """
    Load all documents once for the entire test session.
    """
    return loader.load_documents()


@pytest.fixture(scope="session")
def chunker() -> DocumentChunker:
    """
    Shared chunker.
    """
    return DocumentChunker()


@pytest.fixture(scope="session")
def chunks(chunker, documents):
    """
    Generate chunks once.
    """
    return chunker.chunk_documents(documents)


@pytest.fixture(scope="session")
def retriever() -> EnterpriseRetriever:
    """
    Shared retriever.
    """
    return EnterpriseRetriever()


@pytest.fixture(scope="session")
def client():
    """
    FastAPI test client.
    """
    return TestClient(app)
