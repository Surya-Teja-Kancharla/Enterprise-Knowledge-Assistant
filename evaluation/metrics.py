"""
Enterprise Knowledge Assistant
Evaluation Metrics

Contains reusable metric calculations for
benchmarking the RAG pipeline.
"""

from __future__ import annotations

from typing import Iterable


def document_accuracy(
    expected_document: str,
    retrieved_documents: Iterable[str],
) -> bool:
    """
    Check whether the expected document
    appears in the retrieved documents.
    """

    return expected_document in retrieved_documents


def page_accuracy(
    expected_document: str,
    expected_page: int,
    retrieved_chunks,
) -> bool:
    """
    Check whether the expected page
    of the expected document is retrieved.
    """

    for chunk in retrieved_chunks:

        if (
            chunk.document == expected_document
            and chunk.page == expected_page
        ):
            return True

    return False


def groundedness(
    expected_document: str,
    retrieved_documents: Iterable[str],
) -> bool:
    """
    Groundedness is satisfied if the answer
    is supported by the expected document.
    """

    return expected_document in retrieved_documents


def keyword_accuracy(
    expected_keywords: list[str],
    retrieved_chunks,
) -> float:
    """
    Calculate keyword overlap between
    expected keywords and retrieved text.
    """

    if not expected_keywords:
        return 0.0

    corpus = " ".join(
        chunk.text.lower()
        for chunk in retrieved_chunks
    )

    hits = sum(
        1
        for keyword in expected_keywords
        if keyword.lower() in corpus
    )

    return hits / len(expected_keywords)


def retrieval_precision(
    expected_document: str,
    retrieved_documents: Iterable[str],
) -> float:
    """
    Precision =
    Relevant Retrieved /
    Total Retrieved
    """

    retrieved_documents = list(retrieved_documents)

    if not retrieved_documents:
        return 0.0

    relevant = sum(
        1
        for doc in retrieved_documents
        if doc == expected_document
    )

    return relevant / len(retrieved_documents)


def latency_ms(
    start_time: float,
    end_time: float,
) -> float:
    """
    Return latency in milliseconds.
    """

    return (end_time - start_time) * 1000
