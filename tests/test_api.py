"""
Enterprise Knowledge Assistant
FastAPI Unit Tests
"""

from __future__ import annotations


def test_root_endpoint(client):
    """
    Root endpoint should return
    application information.
    """

    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert "application" in data
    assert "status" in data

    assert data["status"].lower() == "running"


def test_health_endpoint(client):
    """
    Health endpoint should report
    application status.
    """

    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert "status" in data
    assert "embedding_model" in data
    assert "llm_model" in data

    assert data["status"].lower() == "healthy"


def test_ask_endpoint(client):
    """
    Ask endpoint should answer
    a valid question.
    """

    response = client.post(
        "/ask",
        json={
            "question": "What is the password policy?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "answer" in data
    assert "sources" in data
    assert "confidence" in data
    assert "latency" in data
    assert "retrieved_documents" in data

    assert isinstance(data["answer"], str)
    assert isinstance(data["sources"], list)


def test_invalid_route(client):
    """
    Unknown routes should return 404.
    """

    response = client.get("/invalid-route")

    assert response.status_code == 404


def test_validation_error(client):
    """
    Missing request body should
    return validation error.
    """

    response = client.post(
        "/ask",
        json={},
    )

    assert response.status_code == 422


def test_invalid_payload(client):
    """
    Invalid data types should fail.
    """

    response = client.post(
        "/ask",
        json={
            "question": 12345
        },
    )

    assert response.status_code == 422


def test_empty_question(client):
    """
    Empty question should return either
    validation error or a valid response,
    depending on API implementation.
    """

    response = client.post(
        "/ask",
        json={
            "question": ""
        },
    )

    assert response.status_code in (200, 400, 422)
