"""
Enterprise Knowledge Assistant
Loader Unit Tests
"""

from __future__ import annotations

from ingestion.parsers.loader import PDFLoader


def test_loader_initializes(loader):
    """
    Loader should initialize successfully.
    """
    assert isinstance(loader, PDFLoader)


def test_pdfs_discovered(documents):
    """
    All PDFs should be loaded.
    """
    assert len(documents) > 0


def test_pages_extracted(documents):
    """
    At least one page should be extracted.
    """
    assert len(documents) > 0


def test_metadata_exists(documents):
    """
    Every page should contain metadata.
    """

    for page in documents:
        metadata = page.metadata

        assert metadata is not None

        assert "source" in metadata
        assert "page" in metadata


def test_statistics_generated(loader):
    """
    Loader statistics should exist after loading.
    """

    stats = loader.statistics

    assert isinstance(stats, dict)

    assert stats["documents"] > 0
    assert stats["pages"] > 0
    assert stats["characters"] > 0


def test_empty_pages_skipped(documents):
    """
    No loaded page should contain empty text.
    """

    for page in documents:
        assert page.text.strip() != ""
