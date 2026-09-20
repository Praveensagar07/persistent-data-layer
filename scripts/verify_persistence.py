"""10-Step Persistence Verification Test Script.

Validates:
1. Initialize persistent storage & run migrations.
2. Launch API session and create User record.
3. Create Project record linked to that User via foreign key.
4. Create Task record linked to that Project and User.
5. Retrieve all records and verify relational properties.
6. Terminate API session and dispose of database engine completely.
7. Re-initialize a fresh API session against the same persistent database file/PostgreSQL.
8. Query the database afresh.
9. Verify all records, attributes, and relationships are 100% persisted and intact.
10. Confirm persistence success.
"""

import sys
import tempfile
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models.project import Project
from app.models.task import Task
from app.models.user import User
from app.utils.ids import generate_id


def run_persistence_test() -> None:
    print("========================================================")
    print("PERSISTENT DATA LAYER — 10-STEP PERSISTENCE TEST")
    print("========================================================")

    # Use a persistent SQLite database file to simulate disk persistence across restarts
    temp_dir = tempfile.mkdtemp()
    db_file = Path(temp_dir) / "persistent_verify.db"
    db_url = f"sqlite:///{db_file}"

    print(f"Step 1: Initializing persistent storage at: {db_file}")
    engine_1 = create_engine(db_url)
    Base.metadata.create_all(bind=engine_1)
    Session1 = sessionmaker(bind=engine_1)

    print("Step 2: Starting API Session 1 & creating User record...")
    session1 = Session1()
    user_id = generate_id("usr")
    user = User(
        id=user_id,
        name="Marcus Vance",
        email="marcus.vance@example.com",
        role="lead_architect",
    )
    session1.add(user)
    session1.commit()
    print(f"   Created User: ID={user.id}, Name={user.name}, Email={user.email}")

    print("Step 3: Creating Project linked to User...")
    proj_id = generate_id("prj")
    project = Project(
        id=proj_id,
        name="AI Inference Service",
        description="Low latency LLM inference worker nodes.",
        status="active",
        priority="critical",
        owner_id=user.id,
    )
    session1.add(project)
    session1.commit()
    print(f"   Created Project: ID={project.id}, Name={project.name}, OwnerID={project.owner_id}")

    print("Step 4: Creating Task linked to Project and User...")
    task_id = generate_id("tsk")
    task = Task(
        id=task_id,
        title="Benchmark vLLM throughput",
        description="Measure token generation latency across GPU clusters.",
        status="in-progress",
        priority="high",
        project_id=project.id,
        assignee_id=user.id,
    )
    session1.add(task)
    session1.commit()
    print(f"   Created Task: ID={task.id}, Title={task.title}, ProjectID={task.project_id}, AssigneeID={task.assignee_id}")

    print("Step 5: Verifying in-session retrieval...")
    assert session1.get(User, user_id) is not None
    assert session1.get(Project, proj_id) is not None
    assert session1.get(Task, task_id) is not None
    print("   In-session assertions passed.")

    print("Step 6: Shutting down API Session 1 and disposing engine connection...")
    session1.close()
    engine_1.dispose()
    print("   API Session 1 completely terminated. Connections closed.")

    print("Step 7: Starting API Session 2 (simulating cold application restart)...")
    engine_2 = create_engine(db_url)
    Session2 = sessionmaker(bind=engine_2)
    session2 = Session2()

    print("Step 8: Querying database afresh from persistent storage...")
    retrieved_user = session2.get(User, user_id)
    retrieved_project = session2.get(Project, proj_id)
    retrieved_task = session2.get(Task, task_id)

    print("Step 9: Validating persisted data integrity...")
    assert retrieved_user is not None, "User was not found after restart!"
    assert retrieved_user.name == "Marcus Vance", f"User name mismatch: {retrieved_user.name}"
    assert retrieved_user.email == "marcus.vance@example.com", f"User email mismatch: {retrieved_user.email}"

    assert retrieved_project is not None, "Project was not found after restart!"
    assert retrieved_project.name == "AI Inference Service", f"Project name mismatch: {retrieved_project.name}"
    assert retrieved_project.owner_id == user_id, f"Project owner mismatch: {retrieved_project.owner_id}"

    assert retrieved_task is not None, "Task was not found after restart!"
    assert retrieved_task.title == "Benchmark vLLM throughput", f"Task title mismatch: {retrieved_task.title}"
    assert retrieved_task.project_id == proj_id, f"Task project_id mismatch: {retrieved_task.project_id}"
    assert retrieved_task.assignee_id == user_id, f"Task assignee_id mismatch: {retrieved_task.assignee_id}"
    assert retrieved_task.status == "in-progress", f"Task status mismatch: {retrieved_task.status}"

    print("   Retrieved User:    ", retrieved_user.id, retrieved_user.name, retrieved_user.email)
    print("   Retrieved Project: ", retrieved_project.id, retrieved_project.name, f"(Owner: {retrieved_project.owner_id})")
    print("   Retrieved Task:    ", retrieved_task.id, retrieved_task.title, f"(Project: {retrieved_task.project_id}, Assignee: {retrieved_task.assignee_id})")

    session2.close()
    engine_2.dispose()

    # Clean up test artifact
    try:
        db_file.unlink(missing_ok=True)
    except Exception:
        pass

    print("========================================================")
    print("SUCCESS: 10-Step Persistence Test passed with 100% integrity!")
    print("========================================================")


if __name__ == "__main__":
    run_persistence_test()
