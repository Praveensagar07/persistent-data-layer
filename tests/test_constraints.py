"""Tests verifying database-level schema constraints."""

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models.project import Project
from app.models.task import Task
from app.models.user import User
from app.utils.ids import generate_id


def test_db_unique_email_constraint() -> None:
    """Direct database test ensuring duplicate email raises IntegrityError."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    u1 = User(id=generate_id("usr"), name="User 1", email="duplicate@example.com")
    session.add(u1)
    session.commit()

    u2 = User(id=generate_id("usr"), name="User 2", email="duplicate@example.com")
    session.add(u2)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_db_check_constraints_project_status() -> None:
    """Direct database test ensuring invalid project status violates CHECK constraint."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    user = User(id=generate_id("usr"), name="Owner", email="owner@example.com")
    session.add(user)
    session.commit()

    proj = Project(
        id=generate_id("prj"),
        name="Invalid Status Proj",
        status="invalid_status_value",  # fails check constraint
        priority="medium",
        owner_id=user.id,
    )
    session.add(proj)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_db_check_constraints_task_status() -> None:
    """Direct database test ensuring invalid task status violates CHECK constraint."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    user = User(id=generate_id("usr"), name="Owner", email="owner@example.com")
    session.add(user)
    session.commit()

    proj = Project(
        id=generate_id("prj"),
        name="Valid Proj",
        status="active",
        priority="medium",
        owner_id=user.id,
    )
    session.add(proj)
    session.commit()

    task = Task(
        id=generate_id("tsk"),
        title="Invalid Status Task",
        status="bogus_status",  # fails check constraint
        priority="medium",
        project_id=proj.id,
    )
    session.add(task)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()
