"""Tests verifying persistent querying, pagination, and multi-field filters."""

import pytest
from fastapi.testclient import TestClient


def test_seeded_data_retrieval(seeded_client: TestClient) -> None:
    """Verify seeded dataset is queryable via REST endpoints."""
    users_res = seeded_client.get("/api/v1/users")
    assert users_res.status_code == 200
    assert users_res.json()["meta"]["total"] >= 4

    projects_res = seeded_client.get("/api/v1/projects")
    assert projects_res.status_code == 200
    assert projects_res.json()["meta"]["total"] >= 4

    tasks_res = seeded_client.get("/api/v1/tasks")
    assert tasks_res.status_code == 200
    assert tasks_res.json()["meta"]["total"] >= 11


def test_filter_tasks_by_status(seeded_client: TestClient) -> None:
    """Filter tasks by status=in-progress."""
    res = seeded_client.get("/api/v1/tasks?status=in-progress")
    assert res.status_code == 200
    for task in res.json()["data"]:
        assert task["status"] == "in-progress"


def test_filter_tasks_by_priority(seeded_client: TestClient) -> None:
    """Filter tasks by priority=critical."""
    res = seeded_client.get("/api/v1/tasks?priority=critical")
    assert res.status_code == 200
    for task in res.json()["data"]:
        assert task["priority"] == "critical"


def test_filter_projects_by_owner(seeded_client: TestClient) -> None:
    """Filter projects by owner_id=usr_alex_rivera."""
    res = seeded_client.get("/api/v1/projects?owner_id=usr_alex_rivera")
    assert res.status_code == 200
    for project in res.json()["data"]:
        assert project["owner_id"] == "usr_alex_rivera"


def test_pagination_parameters(seeded_client: TestClient) -> None:
    """Validate skip and limit pagination parameters."""
    res = seeded_client.get("/api/v1/tasks?skip=2&limit=3")
    assert res.status_code == 200
    data = res.json()
    assert len(data["data"]) == 3
    assert data["meta"]["skip"] == 2
    assert data["meta"]["limit"] == 3
