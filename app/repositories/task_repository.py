"""Task SQLAlchemy repository implementation."""

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.task import Task


class TaskRepository:
    """Relational data access layer for Task entities."""

    def __init__(self, db: Session = Depends(get_db)) -> None:
        self.db = db

    def get_by_id(self, task_id: str) -> Task | None:
        """Find task by primary key ID."""
        return self.db.get(Task, task_id)

    def list_tasks(
        self,
        skip: int = 0,
        limit: int = 20,
        status: str | None = None,
        priority: str | None = None,
        project_id: str | None = None,
        assignee_id: str | None = None,
    ) -> tuple[list[Task], int]:
        """List paginated tasks matching multiple optional filters."""
        base_query = select(Task)
        count_query = select(func.count()).select_from(Task)

        if status:
            target_status = status.strip().lower()
            base_query = base_query.where(func.lower(Task.status) == target_status)
            count_query = count_query.where(func.lower(Task.status) == target_status)

        if priority:
            target_priority = priority.strip().lower()
            base_query = base_query.where(func.lower(Task.priority) == target_priority)
            count_query = count_query.where(func.lower(Task.priority) == target_priority)

        if project_id:
            base_query = base_query.where(Task.project_id == project_id.strip())
            count_query = count_query.where(Task.project_id == project_id.strip())

        if assignee_id:
            base_query = base_query.where(Task.assignee_id == assignee_id.strip())
            count_query = count_query.where(Task.assignee_id == assignee_id.strip())

        total = self.db.execute(count_query).scalar_one()
        stmt = base_query.order_by(Task.created_at.desc()).offset(skip).limit(limit)
        items = list(self.db.execute(stmt).scalars().all())
        return items, total

    def create(self, task: Task) -> Task:
        """Persist a newly created task."""
        self.db.add(task)
        self.db.flush()
        self.db.refresh(task)
        return task

    def update(self, task: Task) -> Task:
        """Persist modifications to an existing task."""
        self.db.flush()
        self.db.refresh(task)
        return task

    def delete(self, task_id: str) -> bool:
        """Delete task by ID."""
        task = self.get_by_id(task_id)
        if task:
            self.db.delete(task)
            self.db.flush()
            return True
        return False

    def count(self) -> int:
        """Total task count in database."""
        stmt = select(func.count()).select_from(Task)
        return self.db.execute(stmt).scalar_one()
