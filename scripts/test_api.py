"""
Enterprise Knowledge Assistant
FastAPI API Tester

Tests all public API endpoints.

Run

python scripts/test_api.py
"""

from __future__ import annotations

import sys
import time
from typing import Any

import requests


BASE_URL = "http://127.0.0.1:8000"

TIMEOUT = 120

TOTAL_TESTS = 0
PASSED_TESTS = 0


# =====================================================================
# Helpers
# =====================================================================


def heading(title: str) -> None:

    print()

    print("=" * 80)

    print(title)

    print("=" * 80)


def success(message: str) -> None:

    global PASSED_TESTS

    PASSED_TESTS += 1

    print(f"[PASS] {message}")


def failure(message: str) -> None:

    print(f"[FAIL] {message}")


def check(
    condition: bool,
    message: str,
) -> None:

    global TOTAL_TESTS

    TOTAL_TESTS += 1

    if condition:

        success(message)

    else:

        failure(message)


# =====================================================================
# Root
# =====================================================================


def test_root() -> None:

    heading("ROOT ENDPOINT")

    response = requests.get(

        f"{BASE_URL}/",

        timeout=TIMEOUT,

    )

    check(
        response.status_code == 200,
        "Status Code == 200",
    )

    data = response.json()

    check(
        "application" in data,
        "Application present",
    )

    check(
        "status" in data,
        "Status present",
    )


# =====================================================================
# Health
# =====================================================================


def test_health() -> None:

    heading("HEALTH ENDPOINT")

    response = requests.get(

        f"{BASE_URL}/health",

        timeout=TIMEOUT,

    )

    check(
        response.status_code == 200,
        "Status Code == 200",
    )

    data = response.json()

    check(
        data["status"] == "healthy",
        "Application healthy",
    )

    check(
        "embedding_model" in data,
        "Embedding model returned",
    )

    check(
        "llm_model" in data,
        "LLM model returned",
    )


# =====================================================================
# Docs
# =====================================================================


def test_docs() -> None:

    heading("SWAGGER")

    response = requests.get(

        f"{BASE_URL}/docs",

        timeout=TIMEOUT,

    )

    check(
        response.status_code == 200,
        "Swagger available",
    )


# =====================================================================
# Ask
# =====================================================================


def test_ask() -> None:

    heading("ASK ENDPOINT")

    payload = {

        "question": "What is the password policy?"

    }

    start = time.perf_counter()

    response = requests.post(

        f"{BASE_URL}/ask",

        json=payload,

        timeout=TIMEOUT,

    )

    elapsed = round(

        time.perf_counter() - start,

        2,

    )

    check(
        response.status_code == 200,
        "Status Code == 200",
    )

    data: dict[str, Any] = response.json()

    check(
        "answer" in data,
        "Answer returned",
    )

    check(
        "sources" in data,
        "Sources returned",
    )

    check(
        "confidence" in data,
        "Confidence returned",
    )

    print()

    print("Latency")

    print(f"{elapsed:.2f} sec")

    print()

    print("Answer")

    print("-" * 80)

    print(data["answer"])

    print("-" * 80)

    print()

    print("Sources")

    for source in data["sources"]:

        print(

            f"- {source['document']} "

            f"(Page {source['page']})"

        )


# =====================================================================
# Invalid Request
# =====================================================================


def test_invalid_request() -> None:

    heading("INVALID REQUEST")

    payload = {

        "invalid": "question"

    }

    response = requests.post(

        f"{BASE_URL}/ask",

        json=payload,

        timeout=TIMEOUT,

    )

    check(
        response.status_code == 422,
        "Validation works",
    )


# =====================================================================
# Summary
# =====================================================================


def summary() -> None:

    heading("SUMMARY")

    print(

        f"Passed : {PASSED_TESTS}/{TOTAL_TESTS}"

    )

    if PASSED_TESTS == TOTAL_TESTS:

        print()

        print("ALL TESTS PASSED")

    else:

        print()

        print("SOME TESTS FAILED")


# =====================================================================
# Main
# =====================================================================


def main() -> None:

    heading("ENTERPRISE KNOWLEDGE ASSISTANT API TEST")

    try:

        requests.get(

            BASE_URL,

            timeout=5,

        )

    except requests.ConnectionError:

        print()

        print("FastAPI server is not running.")

        print()

        print(

            "Start using:\n"

            "uvicorn app.api.main:app --reload"

        )

        sys.exit(1)

    test_root()

    test_health()

    test_docs()

    test_ask()

    test_invalid_request()

    summary()


if __name__ == "__main__":

    main()