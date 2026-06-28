"""
Enterprise Knowledge Assistant

Test Runner

Hour 6 - Retrieval

Pipeline

Load Vector Database
        ↓
Retriever
        ↓
MMR Search
        ↓
Top K Results
        ↓
Print Sources
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.logger import configure_logger
from retrieval.retrieval import EnterpriseRetriever


def divider(title: str) -> None:
    """
    Print section divider.
    """

    print()
    print("=" * 80)
    print(title)
    print("=" * 80)


def print_result(result, index: int) -> None:
    """
    Pretty-print one retrieved chunk.
    """

    print(f"Result #{index}")

    print(f"Score      : {result.score:.4f}")

    print(f"Document   : {result.document}")

    print(f"Category   : {result.category}")

    print(f"Page       : {result.page}")

    print(f"Chunk      : {result.chunk_number}")

    print(f"Chunk ID   : {result.chunk_id}")

    print()

    preview = result.text.replace("\n", " ")

    preview = preview[:350]

    print("Preview")

    print("-" * 20)

    print(preview)

    print()

    print("-" * 80)


def main() -> None:

    configure_logger()

    divider("INITIALIZING RETRIEVER")

    retriever = EnterpriseRetriever()

    retriever.print_summary()

    print()

    print(
        "Health Check :",
        retriever.health_check(),
    )

    print()

    print(
        "Indexed Vectors :",
        len(retriever),
    )

    divider("MMR RETRIEVAL TEST")

    queries = [

        "How do I reset my password?",

        "How many casual leaves are allowed?",

        "What is GDPR?",

        "How do I create a customer in NovaCRM?",

        "Explain incident response procedure.",

    ]

    for query in queries:

        print()

        print("=" * 80)

        print(f"QUERY : {query}")

        print("=" * 80)

        response = retriever.retrieve(
            query
        )

        print()

        print(
            f"Search Type : {response.search_type}"
        )

        print(
            f"Top K : {response.top_k}"
        )

        print(
            f"Latency : {response.latency_ms:.2f} ms"
        )

        print(
            f"Average Score : {response.average_score:.4f}"
        )

        print(
            f"Results : {response.result_count}"
        )

        print()

        for i, chunk in enumerate(

            response.retrieved_chunks,

            start=1,

        ):

            print_result(

                chunk,

                i,

            )

    divider("CATEGORY FILTER TEST")

    response = retriever.retrieve_category(

        query="Leave policy",

        category="hr",

    )

    print(

        f"Retrieved {response.result_count} HR chunks."

    )

    divider("DOCUMENT FILTER TEST")

    response = retriever.retrieve_document(

        query="Authentication",

        document="Developer Guide.pdf",

    )

    print(

        f"Retrieved {response.result_count} chunks."

    )

    divider("RETRIEVER STATISTICS")

    statistics = retriever.export_statistics()

    for key, value in statistics.items():

        print(f"{key:25}: {value}")

    divider("FINAL SUMMARY")

    retriever.print_summary()

    divider("HOUR 6 COMPLETED SUCCESSFULLY")


if __name__ == "__main__":
    main()
