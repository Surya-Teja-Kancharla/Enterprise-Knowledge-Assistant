"""
Enterprise Knowledge Assistant

End-to-End RAG Pipeline Test

Tests

Question
    ↓
Retriever
    ↓
Prompt
    ↓
Groq LLM
    ↓
Answer
    ↓
Sources
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------
# Project Root
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

from app.core.logger import configure_logger
from services.rag import RAGService

# ---------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------


def divider(title: str) -> None:

    print()

    print("=" * 80)

    print(title)

    print("=" * 80)


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------


def main() -> None:

    configure_logger()

    divider("INITIALIZING RAG SERVICE")

    rag = RAGService()

    if not rag.health_check():

        print("RAG Service failed health check.")

        return

    rag.print_summary()

    # --------------------------------------------------------------
    # Sample Enterprise Queries
    # --------------------------------------------------------------

    questions = [

        "What is the password policy?",

        "How do I reset my password?",

        "What is the work from home policy?",

        "How do I onboard a new employee?",

        "How does incident response work?",

        "Explain subscription plans.",

        "How do I create a customer in NovaCRM?",

        "What are the GDPR principles?",

        "Explain database backup.",

        "What is quantum computing?",

    ]

    total_start = time.perf_counter()

    for index, question in enumerate(
        questions,
        start=1,
    ):

        divider(
            f"QUESTION {index}"
        )

        response = rag.answer_question(
            question
        )

        rag.print_response(
            response
        )

    total_time = (
        time.perf_counter() - total_start
    ) * 1000

    divider("PIPELINE SUMMARY")

    rag.print_statistics()

    print()

    print(
        f"Total Questions : {len(questions)}"
    )

    print(
        f"Total Runtime   : {total_time:.2f} ms"
    )

    print(
        f"Average Runtime : "
        f"{total_time / len(questions):.2f} ms"
    )

    divider("RAG TEST COMPLETED")


# ---------------------------------------------------------------------

if __name__ == "__main__":
    main()
