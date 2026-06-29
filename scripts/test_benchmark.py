"""
Enterprise Knowledge Assistant
Benchmark Test Runner

Executes the complete evaluation pipeline.
"""

from __future__ import annotations

import sys
from pathlib import Path


# ---------------------------------------------------------------------
# Add project root to Python path
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from evaluation.benchmark import RetrievalBenchmark
from evaluation.report import BenchmarkReport


def main() -> None:

    print("=" * 80)
    print("ENTERPRISE KNOWLEDGE ASSISTANT")
    print("BENCHMARK TEST")
    print("=" * 80)

    benchmark = RetrievalBenchmark()

    summary = benchmark.run()

    report = BenchmarkReport()

    json_report = report.save_json(summary)

    markdown_report = report.save_markdown(summary)

    print()

    report.print_summary(summary)

    print()

    print("=" * 80)
    print("REPORTS GENERATED")
    print("=" * 80)

    print(f"JSON      : {json_report}")
    print(f"Markdown  : {markdown_report}")

    print()

    # ---------------------------------------------------------
    # Basic validation
    # ---------------------------------------------------------

    assert summary["questions"] == 20

    assert summary["document_accuracy"] >= 0

    assert summary["page_accuracy"] >= 0

    assert summary["groundedness"] >= 0

    assert summary["keyword_accuracy"] >= 0

    assert summary["average_latency_ms"] >= 0

    print("All benchmark validations passed.")

    print("=" * 80)


if __name__ == "__main__":
    main()
