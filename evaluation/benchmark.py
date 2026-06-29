"""
Enterprise Knowledge Assistant
Benchmark Evaluation
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from retrieval.retrieval import EnterpriseRetriever

from evaluation.metrics import (
    document_accuracy,
    groundedness,
    keyword_accuracy,
    latency_ms,
    page_accuracy,
    retrieval_precision,
)

BENCHMARK_FILE = Path("evaluation/questions.json")


class RetrievalBenchmark:
    """
    Simple retrieval benchmark.

    Evaluates only the retrieval layer.

    Metrics
    -------
    Retrieval Accuracy
    Document Accuracy
    Page Accuracy
    Average Latency
    """

    def __init__(self) -> None:
        self.retriever = EnterpriseRetriever()

        with open(BENCHMARK_FILE, "r", encoding="utf-8") as f:
            self.questions = json.load(f)

    def run(self) -> dict[str, Any]:
        """
        Execute the benchmark suite.
        """

        total = len(self.questions)

        total_document_accuracy = 0
        total_page_accuracy = 0
        total_groundedness = 0
        total_keyword_accuracy = 0
        total_latency = 0.0
        total_retrieval_precision = 0.0

        results = []

        print("=" * 80)
        print("RUNNING ENTERPRISE KNOWLEDGE ASSISTANT BENCHMARK")
        print("=" * 80)

        for item in self.questions:

            question = item["question"]

            expected_document = item["expected_document"]

            expected_page = item["expected_page"]

            expected_keywords = [
                keyword.lower()
                for keyword in item["keywords"]
            ]

            print()
            print("-" * 80)
            print(question)
            print("-" * 80)

            start = time.perf_counter()

            response = self.retriever.retrieve(question)

            end = time.perf_counter()

            latency = latency_ms(start, end)

            total_latency += latency

            retrieved_documents = [
                chunk.document
                for chunk in response.retrieved_chunks
            ]

            precision = retrieval_precision(
                expected_document,
                retrieved_documents,
            )

            total_retrieval_precision += precision

            retrieved_pages = [
                chunk.page
                for chunk in response.retrieved_chunks
            ]

            # --------------------------------------------------
            # Document Accuracy
            # --------------------------------------------------

            document_match = document_accuracy(
                expected_document,
                retrieved_documents,
            )

            if document_match:
                total_document_accuracy += 1

            # --------------------------------------------------
            # Page Accuracy
            # --------------------------------------------------

            page_match = page_accuracy(
                expected_document,
                expected_page,
                response.retrieved_chunks,
            )

            for chunk in response.retrieved_chunks:

                if (
                    chunk.document == expected_document
                    and chunk.page == expected_page
                ):

                    page_match = True

                    break

            if page_match:
                total_page_accuracy += 1

            # --------------------------------------------------
            # Groundedness
            # --------------------------------------------------

            grounded = groundedness(
                expected_document,
                retrieved_documents,
            )

            if grounded:

                total_groundedness += 1

            # --------------------------------------------------
            # Keyword Accuracy
            # --------------------------------------------------

            combined_text = " ".join(
                chunk.text.lower()
                for chunk in response.retrieved_chunks
            )

            keyword_hits = 0

            for keyword in expected_keywords:

                if keyword in combined_text:

                    keyword_hits += 1

            keyword_score = keyword_accuracy(
                expected_keywords,
                response.retrieved_chunks,
            )

            total_keyword_accuracy += keyword_score

            print(
                f"Document Match : {document_match}"
            )

            print(
                f"Page Match     : {page_match}"
            )

            print(
                f"Grounded       : {grounded}"
            )

            print(
                f"Retrieval Precision : {precision:.2f}"
            )

            print(
                f"Keyword Score  : {keyword_score:.2f}"
            )

            print(
                f"Latency        : {latency:.2f} ms"
            )

            results.append(
                {
                    "question": question,
                    "expected_document": expected_document,
                    "retrieved_documents": retrieved_documents,
                    "document_match": document_match,
                    "page_match": page_match,
                    "grounded": grounded,
                    "retrieval_precision": round(precision, 3),
                    "keyword_accuracy": round(keyword_score, 3),
                    "latency_ms": round(latency, 2),
                }
            )

        summary = {
            "questions": total,
            "document_accuracy": round(total_document_accuracy / total * 100, 2),
            "page_accuracy": round(total_page_accuracy / total * 100, 2),
            "groundedness": round(total_groundedness / total* 100, 2),
            "retrieval_precision": round(total_retrieval_precision / total * 100, 2),
            "keyword_accuracy": round(total_keyword_accuracy / total* 100, 2),
            "average_latency_ms": round(total_latency / total, 2),
            "results": results,
        }

        return summary


def print_summary(summary: dict[str, Any]) -> None:

    print()

    print("=" * 80)
    print("BENCHMARK SUMMARY")
    print("=" * 80)

    print(f"Questions            : {summary['questions']}")

    print(
        f"Document Accuracy    : "
        f"{summary['document_accuracy']:.2f}%"
    )

    print(
        f"Page Accuracy        : "
        f"{summary['page_accuracy']:.2f}%"
    )

    print(
        f"Retrieval Precision  : "
        f"{summary['retrieval_precision']:.2f}%"
    )

    print(
        f"Average Latency      : "
        f"{summary['average_latency_ms']:.2f} ms"
    )


def save_results(summary: dict[str, Any]) -> None:

    output = Path("evaluation/results.json")

    output.parent.mkdir(exist_ok=True)

    with open(output, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)

    print()
    print(f"Results saved to {output}")


def main() -> None:

    benchmark = RetrievalBenchmark()

    summary = benchmark.run()

    print_summary(summary)

    from evaluation.report import BenchmarkReport

    report = BenchmarkReport()

    json_file = report.save_json(summary)

    markdown_file = report.save_markdown(summary)

    report.print_summary(summary)

    print()

    print(f"JSON Report      : {json_file}")

    print(f"Markdown Report  : {markdown_file}")


if __name__ == "__main__":
    main()
