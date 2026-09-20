"""Tests for Task CRUD persistence, workflow states, and foreign key validations."""

import pytest
from fastapi.testclient import TestClient


def test_create_task_success(client: TestClient) -> None:
    """Create task with valid project and assignee."""
    user = client.post(
        "/api/v1/users",
        json={"name": "Task Assignee", "email": "assignee@example.com"},
    ).json()["data"]

    project = client.post(
        "/api/v1/projects",
        json={"name": "Task Platform", "owner_id": user["id"]},
    ).json()["data"]

    payload = {
        "title": "Build authentication module",
        "description": "OAuth2 password flow implementation.",
        "project_id": project["id"],
        "assignee_id": user["id"],
        "status": "todo",
        "priority": "critical",
    }
    res = client.post("/api/v1/tasks", json=payload)
    assert res.status_code == 201
    data = res.json()["data"]
    assert data["title"] == "Build authentication module"
    assert data["project_id"] == project["id"]
    assert data["assignee_id"] == user["id"]
    assert data["status"] == "todo"
    assert data["priority"] == "critical"


def test_create_task_invalid_project_rejected(client: TestClient) -> None:
    """Create task with invalid project ID returns 404."""
    res = client.post(
        "/api/v1/tasks",
        json={"title": "Orphan Task", "project_id": "prj_invalid"},
    )
    assert res.status_code == 404
    assert res.json()["error"]["code"] == "RESOURCE_NOT_FOUND"


def test_create_task_invalid_assignee_rejected(client: TestClient) -> None:
    """Create task with invalid assignee ID returns 404."""
    user = client.post(
        "/api/v1/users",
        json={"name": "Owner", "email": "owner2@example.com"},
    ).json()["data"]

    project = client.post(
        "/api/v1/projects",
        json={"name": "Project 2", "owner_id": user["id"]},
    ).json()["data"]

    res = client.post(
        "/api/v1/tasks",
        json={
            "title": "Task with bad assignee",
            "project_id": project["id"],
            "assignee_id": "usr_invalid",
        },
    )
    assert res.status_code == 404


def test_update_task_status_endpoint(client: TestClient) -> None:
    """Dedicated status endpoint updates task lifecycle progression."""
    user = client.post(
        "/api/v1/users",
        json={"name": "Workflow User", "email": "flow@example.com"},
    ).json()["data"]

    project = client.post(
        "/api/v1/projects",
        json={"name": "Workflow Project", "owner_id": user["id"]},
    ).json()["data"]

    task = client.post(
        "/api/v1/tasks",
        json={"title": "Status Workflow Task", "project_id": project["id"]},
    ).json()["data"]
    assert task["status"] == "todo"

    # Progress to in-progress
    res1 = client.patch(
        f"/api/v1/tasks/{task['id']}/status",
        json={"status": "in-progress"},
    )
    assert res1.status_code == 200
    assert res1.json()["data"]["status"] == "in-progress"

    # Progress to done
    res2 = client.patch(
        f"/api/v1/tasks/{task['id']}/status",
        json={"status": "done"},
    )
    assert res2.status_code == 200
    assert res2.json()["data"]["status"] == "done"


def test_invalid_task_status_rejected(client: TestClient) -> None:
    """Setting an unsupported status returns 422 validation error."""
    user = client.post(
        "/api/v1/users",
        json={"name": "Status User", "email": "status@example.com"},
    ).json()["data"]

    project = client.post(
        "/api/v1/projects",
        json={"name": "Status Project", "owner_id": user["id"]},
    ).json()["data"]

    res = client.post(
        "/api/v1/tasks",
        json={
            "title": "Invalid status task",
            "project_id": project["id"],
            "status": "pending_approval",  # invalid
        },
    )
    assert res.status_code == 422
