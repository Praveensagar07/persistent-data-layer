"""Tests for database relational integrity, foreign key actions, and cascading."""

import pytest
from fastapi.testclient import TestClient


def test_user_deletion_sets_task_assignee_null(client: TestClient) -> None:
    """When an assigned user is deleted, task remains intact but assignee_id becomes NULL."""
    user1 = client.post(
        "/api/v1/users",
        json={"name": "Project Owner", "email": "p_owner@example.com"},
    ).json()["data"]

    user2 = client.post(
        "/api/v1/users",
        json={"name": "Assigned Worker", "email": "worker@example.com"},
    ).json()["data"]

    project = client.post(
        "/api/v1/projects",
        json={"name": "Relationship Project", "owner_id": user1["id"]},
    ).json()["data"]

    task = client.post(
        "/api/v1/tasks",
        json={
            "title": "Worker Task",
            "project_id": project["id"],
            "assignee_id": user2["id"],
        },
    ).json()["data"]
    assert task["assignee_id"] == user2["id"]

    # Delete worker user
    client.delete(f"/api/v1/users/{user2['id']}")

    # Task should still exist, but assignee_id is now None/null
    retrieved = client.get(f"/api/v1/tasks/{task['id']}").json()["data"]
    assert retrieved["id"] == task["id"]
    assert retrieved["assignee_id"] is None


def test_user_deletion_cascades_to_owned_projects(client: TestClient) -> None:
    """When an owner user is deleted, their owned projects and projects' tasks are cleaned up."""
    owner = client.post(
        "/api/v1/users",
        json={"name": "Sole Owner", "email": "sole@example.com"},
    ).json()["data"]

    project = client.post(
        "/api/v1/projects",
        json={"name": "Sole Project", "owner_id": owner["id"]},
    ).json()["data"]

    task = client.post(
        "/api/v1/tasks",
        json={"title": "Sole Task", "project_id": project["id"]},
    ).json()["data"]

    # Delete owner
    client.delete(f"/api/v1/users/{owner['id']}")

    # Project and task must both be gone
    assert client.get(f"/api/v1/projects/{project['id']}").status_code == 404
    assert client.get(f"/api/v1/tasks/{task['id']}").status_code == 404
