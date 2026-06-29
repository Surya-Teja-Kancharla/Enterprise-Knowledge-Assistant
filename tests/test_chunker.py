"""
Enterprise Knowledge Assistant
Chunker Unit Tests
"""

from __future__ import annotations

from ingestion.chunking.chunker import DocumentChunk


def test_chunks_generated(chunks):
    """
    Chunker should generate at least one chunk.
    """

    assert len(chunks) > 0

    assert all(
        isinstance(chunk, DocumentChunk)
        for chunk in chunks
    )


def test_metadata_propagated(chunks):
    """
    Every chunk should preserve source metadata.
    """

    for chunk in chunks:

        metadata = chunk.metadata

        assert metadata is not None

        assert "document" in metadata
        assert "page" in metadata
        assert "category" in metadata
        assert "source" in metadata
        assert "chunk_id" in metadata


def test_unique_chunk_ids(chunks):
    """
    Every generated chunk_id must be unique.
    """

    chunk_ids = [
        chunk.metadata["chunk_id"]
        for chunk in chunks
    ]

    assert len(chunk_ids) == len(set(chunk_ids))


def test_chunk_size_limit(chunks):
    """
    No chunk should exceed the configured chunk size.
    """

    MAX_SIZE = 900

    for chunk in chunks:

        assert len(chunk.text) <= MAX_SIZE


def test_no_empty_chunks(chunks):
    """
    Empty chunks should never be generated.
    """

    for chunk in chunks:

        assert chunk.text.strip() != ""


def test_overlap_respected(chunks):
    """
    Every chunk should store the configured overlap.
    """

    for chunk in chunks:

        assert chunk.metadata["chunk_overlap"] == 150
