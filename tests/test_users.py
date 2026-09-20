"""Tests for User CRUD persistence, validation, and invariants."""

import pytest
from fastapi.testclient import TestClient


def test_create_user_success(client: TestClient) -> None:
    """Validate creating a user stores record in database and returns 201."""
    payload = {
        "name": "Sarah Connor",
        "email": "sarah.connor@example.com",
        "role": "lead_architect",
    }
    res = client.post("/api/v1/users", json=payload)
    assert res.status_code == 201
    body = res.json()["data"]
    assert body["name"] == "Sarah Connor"
    assert body["email"] == "sarah.connor@example.com"
    assert body["role"] == "lead_architect"
    assert body["id"].startswith("usr_")
    assert "created_at" in body
    assert "updated_at" in body


def test_create_user_duplicate_email_rejected(client: TestClient) -> None:
    """Validate duplicate email address returns 409 Conflict."""
    payload = {
        "name": "Alex Rivera",
        "email": "alex.rivera@example.com",
        "role": "admin",
    }
    res1 = client.post("/api/v1/users", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/api/v1/users", json=payload)
    assert res2.status_code == 409
    error = res2.json()["error"]
    assert error["code"] == "DUPLICATE_RESOURCE"


def test_get_user_by_id(client: TestClient) -> None:
    """Retrieve existing user by ID."""
    created = client.post(
        "/api/v1/users",
        json={"name": "Alice Developer", "email": "alice@example.com"},
    ).json()["data"]

    res = client.get(f"/api/v1/users/{created['id']}")
    assert res.status_code == 200
    assert res.json()["data"]["id"] == created["id"]
    assert res.json()["data"]["name"] == "Alice Developer"


def test_get_user_not_found(client: TestClient) -> None:
    """Nonexistent user ID returns 404."""
    res = client.get("/api/v1/users/usr_nonexistent")
    assert res.status_code == 404
    assert res.json()["error"]["code"] == "RESOURCE_NOT_FOUND"


def test_update_user(client: TestClient) -> None:
    """Update name and role of an existing user."""
    created = client.post(
        "/api/v1/users",
        json={"name": "Bob Builder", "email": "bob@example.com"},
    ).json()["data"]

    update_payload = {"name": "Bob Architect", "role": "lead_architect"}
    res = client.patch(f"/api/v1/users/{created['id']}", json=update_payload)
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["name"] == "Bob Architect"
    assert data["role"] == "lead_architect"
    assert data["email"] == "bob@example.com"


def test_delete_user(client: TestClient) -> None:
    """Delete an existing user."""
    created = client.post(
        "/api/v1/users",
        json={"name": "Charlie Chaplin", "email": "charlie@example.com"},
    ).json()["data"]

    del_res = client.delete(f"/api/v1/users/{created['id']}")
    assert del_res.status_code == 200
    assert del_res.json()["data"]["message"] == "User deleted successfully"

    get_res = client.get(f"/api/v1/users/{created['id']}")
    assert get_res.status_code == 404
