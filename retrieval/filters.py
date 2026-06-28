"""
Enterprise Knowledge Assistant

Retrieval Filters

Provides helper utilities for constructing metadata
filters used during semantic retrieval.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class MetadataFilter:
    """
    Builder for metadata filters used during retrieval.
    """

    filters: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """
        Return filter dictionary.
        """

        return dict(self.filters)


# ==========================================================
# Factory Functions
# ==========================================================

def category_filter(
    category: str,
) -> dict[str, Any]:
    """
    Filter by category.
    """

    return {
        "category": category,
    }


def document_filter(
    document: str,
) -> dict[str, Any]:
    """
    Filter by document.
    """

    return {
        "document": document,
    }


def page_filter(
    document: str,
    page: int,
) -> dict[str, Any]:
    """
    Filter by document page.
    """

    return {

        "document": document,

        "page": page,

    }


def chunk_filter(
    chunk_id: str,
) -> dict[str, Any]:
    """
    Filter by chunk identifier.
    """

    return {

        "chunk_id": chunk_id,

    }


def source_filter(
    source: str,
) -> dict[str, Any]:
    """
    Filter by source path.
    """

    return {

        "source": source,

    }


def custom_filter(
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Build a custom metadata filter.

    Example
    -------
    custom_filter(
        category="hr",
        page=5,
    )
    """

    return dict(kwargs)
