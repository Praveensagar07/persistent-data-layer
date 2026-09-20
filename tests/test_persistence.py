"""Tests validating persistent disk storage across engine/process restarts."""

import tempfile
from pathlib import Path
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models.project import Project
from app.models.task import Task
from app.models.user import User
from app.utils.ids import generate_id


def test_data_persistence_across_restart() -> None:
    """Validate data written to database remains intact after closing session and recreating engine."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = Path(tmp_dir) / "persistent_test.db"
        db_url = f"sqlite:///{db_path}"

        # Session 1: Write
        engine1 = create_engine(db_url)
        Base.metadata.create_all(bind=engine1)
        Session1 = sessionmaker(bind=engine1)
        s1 = Session1()

        u_id = generate_id("usr")
        user = User(id=u_id, name="Persistent Person", email="persist@example.com")
        s1.add(user)

        p_id = generate_id("prj")
        project = Project(id=p_id, name="Persistent Project", owner_id=u_id)
        s1.add(project)

        t_id = generate_id("tsk")
        task = Task(id=t_id, title="Persistent Task", project_id=p_id, assignee_id=u_id)
        s1.add(task)

        s1.commit()
        s1.close()
        engine1.dispose()

        # Session 2: Read after cold restart
        engine2 = create_engine(db_url)
        Session2 = sessionmaker(bind=engine2)
        s2 = Session2()

        loaded_user = s2.get(User, u_id)
        assert loaded_user is not None
        assert loaded_user.name == "Persistent Person"
        assert loaded_user.email == "persist@example.com"

        loaded_proj = s2.get(Project, p_id)
        assert loaded_proj is not None
        assert loaded_proj.name == "Persistent Project"
        assert loaded_proj.owner_id == u_id

        loaded_task = s2.get(Task, t_id)
        assert loaded_task is not None
        assert loaded_task.title == "Persistent Task"
        assert loaded_task.project_id == p_id
        assert loaded_task.assignee_id == u_id

        s2.close()
        engine2.dispose()
