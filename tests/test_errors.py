"""Tests verifying standardized error payloads and HTTP status codes."""

import pytest
from fastapi.testclient import TestClient


def test_404_not_found_format(client: TestClient) -> None:
    """Verify 404 response matches standard error envelope."""
    res = client.get("/api/v1/users/usr_doesnotexist")
    assert res.status_code == 404
    error = res.json()["error"]
    assert error["code"] == "RESOURCE_NOT_FOUND"
    assert "not found" in error["message"].lower()


def test_422_validation_error_format(client: TestClient) -> None:
    """Verify invalid body returns 422 with structured field details."""
    res = client.post("/api/v1/users", json={"name": "", "email": "bad_email"})
    assert res.status_code == 422
    error = res.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert len(error["details"]) >= 1


def test_observability_headers(client: TestClient) -> None:
    """Verify responses contain X-Request-ID and X-Process-Time headers."""
    res = client.get("/health")
    assert res.status_code == 200
    assert "X-Request-ID" in res.headers
    assert "X-Process-Time" in res.headers
