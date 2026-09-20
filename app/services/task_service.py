"""Task business service layer."""

from datetime import datetime, timezone
from fastapi import Depends
from app.core.exceptions import ResourceNotFoundError
from app.models.task import Task
from app.repositories.project_repository import ProjectRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository
from app.schemas.task import TaskCreate, TaskStatus, TaskUpdate
from app.utils.ids import generate_id


class TaskService:
    """Business logic orchestrator for Task operations."""

    def __init__(
        self,
        task_repo: TaskRepository = Depends(),
        project_repo: ProjectRepository = Depends(),
        user_repo: UserRepository = Depends(),
    ) -> None:
        self.task_repo = task_repo
        self.project_repo = project_repo
        self.user_repo = user_repo

    def create_task(self, payload: TaskCreate) -> Task:
        """Create task after verifying parent project and assignee exist."""
        project = self.project_repo.get_by_id(payload.project_id)
        if not project:
            raise ResourceNotFoundError(
                message=f"Project with id '{payload.project_id}' does not exist",
                resource_type="Project",
                resource_id=payload.project_id,
            )

        if payload.assignee_id:
            assignee = self.user_repo.get_by_id(payload.assignee_id)
            if not assignee:
                raise ResourceNotFoundError(
                    message=f"Assignee with user id '{payload.assignee_id}' does not exist",
                    resource_type="User",
                    resource_id=payload.assignee_id,
                )

        now = datetime.now(timezone.utc)
        task = Task(
            id=generate_id("tsk"),
            title=payload.title,
            description=payload.description,
            project_id=payload.project_id,
            assignee_id=payload.assignee_id,
            status=payload.status.value if hasattr(payload.status, "value") else str(payload.status),
            priority=payload.priority.value if hasattr(payload.priority, "value") else str(payload.priority),
            due_date=payload.due_date,
            created_at=now,
            updated_at=now,
        )
        return self.task_repo.create(task)

    def get_task(self, task_id: str) -> Task:
        """Fetch task by identifier or raise ResourceNotFoundError."""
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise ResourceNotFoundError(resource_type="Task", resource_id=task_id)
        return task

    def list_tasks(
        self,
        skip: int = 0,
        limit: int = 20,
        status: str | None = None,
        priority: str | None = None,
        project_id: str | None = None,
        assignee_id: str | None = None,
    ) -> tuple[list[Task], int]:
        """List paginated tasks matching optional filters."""
        return self.task_repo.list_tasks(
            skip=skip,
            limit=limit,
            status=status,
            priority=priority,
            project_id=project_id,
            assignee_id=assignee_id,
        )

    def update_task(self, task_id: str, payload: TaskUpdate) -> Task:
        """Update task with relational integrity checks."""
        task = self.get_task(task_id)

        if payload.project_id is not None and payload.project_id != task.project_id:
            project = self.project_repo.get_by_id(payload.project_id)
            if not project:
                raise ResourceNotFoundError(
                    message=f"Project with id '{payload.project_id}' does not exist",
                    resource_type="Project",
                    resource_id=payload.project_id,
                )
            task.project_id = payload.project_id

        if payload.assignee_id is not None and payload.assignee_id != task.assignee_id:
            if payload.assignee_id == "":
                task.assignee_id = None
            else:
                assignee = self.user_repo.get_by_id(payload.assignee_id)
                if not assignee:
                    raise ResourceNotFoundError(
                        message=f"Assignee with user id '{payload.assignee_id}' does not exist",
                        resource_type="User",
                        resource_id=payload.assignee_id,
                    )
                task.assignee_id = payload.assignee_id

        if payload.title is not None:
            task.title = payload.title

        if payload.description is not None:
            task.description = payload.description

        if payload.status is not None:
            task.status = (
                payload.status.value if hasattr(payload.status, "value") else str(payload.status)
            )

        if payload.priority is not None:
            task.priority = (
                payload.priority.value if hasattr(payload.priority, "value") else str(payload.priority)
            )

        if payload.due_date is not None:
            task.due_date = payload.due_date

        task.updated_at = datetime.now(timezone.utc)
        return self.task_repo.update(task)

    def update_task_status(self, task_id: str, new_status: TaskStatus) -> Task:
        """Dedicated update for task lifecycle status."""
        task = self.get_task(task_id)
        task.status = (
            new_status.value if hasattr(new_status, "value") else str(new_status)
        )
        task.updated_at = datetime.now(timezone.utc)
        return self.task_repo.update(task)

    def delete_task(self, task_id: str) -> None:
        """Delete task by identifier or raise ResourceNotFoundError."""
        _ = self.get_task(task_id)
        self.task_repo.delete(task_id)
