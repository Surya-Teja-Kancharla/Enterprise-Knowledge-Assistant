"""
Enterprise Knowledge Assistant
Retriever Unit Tests
"""

from __future__ import annotations

import pytest

from retrieval.models import RetrievedChunk


def test_retrieve_returns_list(retriever):
    """
    Retrieval should always return a list.
    """

    response = retriever.retrieve(
        "What is the password policy?"
    )

    assert response is not None
    assert isinstance(
        response.retrieved_chunks,
        list,
    )


def test_top_k_respected(retriever):
    """
    Retriever should never return
    more than TOP_K results.
    """

    TOP_K = 5

    response = retriever.retrieve(
        "Explain GDPR."
    )

    assert (
        len(response.retrieved_chunks)
        <= TOP_K
    )


def test_results_are_retrieved_chunks(retriever):
    """
    Every retrieved result should
    be a RetrievedChunk.
    """

    response = retriever.retrieve(
        "Employee leave policy"
    )

    assert all(
        isinstance(item, RetrievedChunk)
        for item in response.retrieved_chunks
    )


def test_metadata_exists(retriever):
    """
    Retrieved chunks should preserve metadata.
    """

    response = retriever.retrieve(
        "Password policy"
    )

    assert len(response.retrieved_chunks) > 0

    for chunk in response.retrieved_chunks:
        metadata = chunk.metadata

        assert metadata is not None

        assert "document" in metadata
        assert "page" in metadata
        assert "category" in metadata
        assert "source" in metadata


def test_hybrid_retrieval(retriever):
    """
    Hybrid search should retrieve
    at least one relevant result.
    """

    response = retriever.retrieve(
        "GDPR Article"
    )

    assert len(response.retrieved_chunks) > 0


def test_empty_query_handled(retriever):
    """
    Empty queries should return
    an empty list.
    """

    with pytest.raises(ValueError):
        retriever.retrieve("")


@pytest.mark.parametrize(
    "query",
    [
        "Password policy",
        "Leave policy",
        "API authentication",
        "Subscription plans",
        "Incident response",
    ],
)
def test_multiple_queries(query, retriever):
    """
    Various enterprise queries
    should execute successfully.
    """

    response = retriever.retrieve(query)

    assert response is not None
    assert isinstance(
        response.retrieved_chunks,
        list,
    )
