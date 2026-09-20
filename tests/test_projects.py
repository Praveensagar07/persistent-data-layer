"""Tests for Project CRUD persistence, relationships, and validation."""

import pytest
from fastapi.testclient import TestClient


def test_create_project_success(client: TestClient) -> None:
    """Create a project referencing a valid owner."""
    user = client.post(
        "/api/v1/users",
        json={"name": "Project Owner", "email": "owner@example.com"},
    ).json()["data"]

    payload = {
        "name": "Cloud Migration",
        "description": "Migrate on-prem servers to AWS.",
        "status": "active",
        "priority": "high",
        "owner_id": user["id"],
    }
    res = client.post("/api/v1/projects", json=payload)
    assert res.status_code == 201
    body = res.json()["data"]
    assert body["name"] == "Cloud Migration"
    assert body["owner_id"] == user["id"]
    assert body["id"].startswith("prj_")


def test_create_project_invalid_owner_rejected(client: TestClient) -> None:
    """Create project referencing nonexistent owner returns 404."""
    payload = {
        "name": "Orphan Project",
        "owner_id": "usr_invalid_id",
    }
    res = client.post("/api/v1/projects", json=payload)
    assert res.status_code == 404
    assert res.json()["error"]["code"] == "RESOURCE_NOT_FOUND"


def test_update_project(client: TestClient) -> None:
    """Update project status and description."""
    user = client.post(
        "/api/v1/users",
        json={"name": "Dev Lead", "email": "lead@example.com"},
    ).json()["data"]

    project = client.post(
        "/api/v1/projects",
        json={"name": "Sprint 1", "owner_id": user["id"]},
    ).json()["data"]

    patch_res = client.patch(
        f"/api/v1/projects/{project['id']}",
        json={"status": "completed", "priority": "critical"},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["data"]["status"] == "completed"
    assert patch_res.json()["data"]["priority"] == "critical"


def test_delete_project_cascades_to_tasks(client: TestClient) -> None:
    """Deleting a project automatically cascades to delete all associated tasks."""
    user = client.post(
        "/api/v1/users",
        json={"name": "Cascade Tester", "email": "cascade@example.com"},
    ).json()["data"]

    project = client.post(
        "/api/v1/projects",
        json={"name": "Parent Project", "owner_id": user["id"]},
    ).json()["data"]

    task = client.post(
        "/api/v1/tasks",
        json={"title": "Child Task", "project_id": project["id"]},
    ).json()["data"]

    # Verify task exists
    assert client.get(f"/api/v1/tasks/{task['id']}").status_code == 200

    # Delete parent project
    del_res = client.delete(f"/api/v1/projects/{project['id']}")
    assert del_res.status_code == 200

    # Child task must no longer exist (cascaded delete)
    assert client.get(f"/api/v1/tasks/{task['id']}").status_code == 404
