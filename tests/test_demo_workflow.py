"""End-to-end integration workflow test."""

import pytest
from fastapi.testclient import TestClient


def test_complete_project_lifecycle_workflow(client: TestClient) -> None:
    """Complete user story:
    1. Register new developer
    2. Create new initiative project
    3. Add 3 tasks (todo, in-progress, done)
    4. Transition task states
    5. Query summary
    6. Clean up
    """
    # 1. Register developer
    user = client.post(
        "/api/v1/users",
        json={"name": "Devin AI Engineer", "email": "devin@example.com", "role": "developer"},
    ).json()["data"]

    # 2. Create project
    project = client.post(
        "/api/v1/projects",
        json={
            "name": "Autonomous Code Generator",
            "description": "Agentic coding engine for software teams.",
            "status": "active",
            "priority": "critical",
            "owner_id": user["id"],
        },
    ).json()["data"]

    # 3. Create tasks
    task1 = client.post(
        "/api/v1/tasks",
        json={
            "title": "Context Window Expander",
            "project_id": project["id"],
            "assignee_id": user["id"],
            "status": "todo",
            "priority": "high",
        },
    ).json()["data"]

    task2 = client.post(
        "/api/v1/tasks",
        json={
            "title": "Tool Call Parser",
            "project_id": project["id"],
            "assignee_id": user["id"],
            "status": "in-progress",
            "priority": "critical",
        },
    ).json()["data"]

    # 4. Advance task1 from todo to in-progress
    patch_res = client.patch(
        f"/api/v1/tasks/{task1['id']}/status",
        json={"status": "in-progress"},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["data"]["status"] == "in-progress"

    # Advance task2 to done
    patch_res2 = client.patch(
        f"/api/v1/tasks/{task2['id']}/status",
        json={"status": "done"},
    )
    assert patch_res2.status_code == 200
    assert patch_res2.json()["data"]["status"] == "done"

    # 5. Query tasks for project
    tasks_res = client.get(f"/api/v1/tasks?project_id={project['id']}")
    assert tasks_res.status_code == 200
    assert len(tasks_res.json()["data"]) == 2

    # 6. Delete project
    del_res = client.delete(f"/api/v1/projects/{project['id']}")
    assert del_res.status_code == 200
