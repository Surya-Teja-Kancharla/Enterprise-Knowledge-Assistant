"""
Enterprise Knowledge Assistant
Benchmark Report Generator
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


class BenchmarkReport:
    """
    Generates benchmark reports.

    Output Formats
    --------------
    - JSON
    - Markdown
    """

    REPORT_DIR = Path("evaluation/reports")

    def __init__(self) -> None:

        self.REPORT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

    # --------------------------------------------------------
    # JSON
    # --------------------------------------------------------

    def save_json(
        self,
        summary: dict[str, Any],
    ) -> Path:

        filename = (
            f"benchmark_"
            f"{datetime.now():%Y%m%d_%H%M%S}.json"
        )

        output = self.REPORT_DIR / filename

        with open(
            output,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                summary,
                f,
                indent=4,
            )

        return output

    # --------------------------------------------------------
    # Markdown
    # --------------------------------------------------------

    def save_markdown(
        self,
        summary: dict[str, Any],
    ) -> Path:

        filename = (
            f"benchmark_"
            f"{datetime.now():%Y%m%d_%H%M%S}.md"
        )

        output = self.REPORT_DIR / filename

        with open(
            output,
            "w",
            encoding="utf-8",
        ) as f:

            f.write("# Enterprise Knowledge Assistant Benchmark\n\n")

            f.write(
                f"Generated: {datetime.now():%Y-%m-%d %H:%M:%S}\n\n"
            )

            f.write("---\n\n")

            f.write("## Overall Results\n\n")

            metrics = [

                ("Questions", summary["questions"]),

                ("Document Accuracy", f"{summary['document_accuracy']}%"),

                ("Page Accuracy", f"{summary['page_accuracy']}%"),

                ("Groundedness", f"{summary['groundedness']}%"),

                ("Keyword Accuracy", f"{summary['keyword_accuracy']}%"),

                (
                    "Average Latency",
                    f"{summary['average_latency_ms']} ms",
                ),
            ]

            f.write("| Metric | Value |\n")
            f.write("|--------|------:|\n")

            for metric, value in metrics:

                f.write(
                    f"| {metric} | {value} |\n"
                )

            f.write("\n---\n\n")

            f.write("## Question-wise Results\n\n")

            f.write(
                "| Question | Doc | Page | Grounded | Precision | Latency |\n"
            )

            f.write(
                "|----------|:---:|:----:|:---------:|----------:|---------:|\n"
            )

            for result in summary["results"]:

                f.write(

                    "| "

                    f"{result['question']} | "

                    f"{'✅' if result['document_match'] else '❌'} | "

                    f"{'✅' if result['page_match'] else '❌'} | "

                    f"{'✅' if result['grounded'] else '❌'} | "

                    f"{result.get('retrieval_precision',0):.2f} | "

                    f"{result['latency_ms']:.2f} ms |\n"

                )

        return output

    # --------------------------------------------------------
    # Console
    # --------------------------------------------------------

    @staticmethod
    def print_summary(
        summary: dict[str, Any],
    ) -> None:

        print()

        print("=" * 80)
        print("ENTERPRISE KNOWLEDGE ASSISTANT")
        print("BENCHMARK REPORT")
        print("=" * 80)

        print(
            f"Questions             : {summary['questions']}"
        )

        print(
            f"Document Accuracy     : {summary['document_accuracy']:.2f}%"
        )

        print(
            f"Page Accuracy         : {summary['page_accuracy']:.2f}%"
        )

        print(
            f"Groundedness          : {summary['groundedness']:.2f}%"
        )

        print(
            f"Keyword Accuracy      : {summary['keyword_accuracy']:.2f}%"
        )

        print(
            f"Average Latency       : {summary['average_latency_ms']:.2f} ms"
        )

        print("=" * 80)
