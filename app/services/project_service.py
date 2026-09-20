"""Project business service layer."""

from datetime import datetime, timezone
from fastapi import Depends
from app.core.exceptions import ResourceNotFoundError
from app.models.project import Project
from app.repositories.project_repository import ProjectRepository
from app.repositories.user_repository import UserRepository
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.utils.ids import generate_id


class ProjectService:
    """Business logic orchestrator for Project operations."""

    def __init__(
        self,
        project_repo: ProjectRepository = Depends(),
        user_repo: UserRepository = Depends(),
    ) -> None:
        self.project_repo = project_repo
        self.user_repo = user_repo

    def create_project(self, payload: ProjectCreate) -> Project:
        """Create project after verifying the owner user exists."""
        owner = self.user_repo.get_by_id(payload.owner_id)
        if not owner:
            raise ResourceNotFoundError(
                message=f"Project owner with user id '{payload.owner_id}' does not exist",
                resource_type="User",
                resource_id=payload.owner_id,
            )

        now = datetime.now(timezone.utc)
        project = Project(
            id=generate_id("prj"),
            name=payload.name,
            description=payload.description,
            status=payload.status.value if hasattr(payload.status, "value") else str(payload.status),
            priority=payload.priority.value if hasattr(payload.priority, "value") else str(payload.priority),
            owner_id=payload.owner_id,
            created_at=now,
            updated_at=now,
        )
        return self.project_repo.create(project)

    def get_project(self, project_id: str) -> Project:
        """Fetch project by identifier or raise ResourceNotFoundError."""
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise ResourceNotFoundError(resource_type="Project", resource_id=project_id)
        return project

    def list_projects(
        self,
        skip: int = 0,
        limit: int = 20,
        owner_id: str | None = None,
        status: str | None = None,
    ) -> tuple[list[Project], int]:
        """List paginated projects with optional filters."""
        return self.project_repo.list_projects(
            skip=skip,
            limit=limit,
            owner_id=owner_id,
            status=status,
        )

    def update_project(self, project_id: str, payload: ProjectUpdate) -> Project:
        """Update existing project fields with owner existence validation."""
        project = self.get_project(project_id)

        if payload.owner_id is not None and payload.owner_id != project.owner_id:
            owner = self.user_repo.get_by_id(payload.owner_id)
            if not owner:
                raise ResourceNotFoundError(
                    message=f"Project owner with user id '{payload.owner_id}' does not exist",
                    resource_type="User",
                    resource_id=payload.owner_id,
                )
            project.owner_id = payload.owner_id

        if payload.name is not None:
            project.name = payload.name

        if payload.description is not None:
            project.description = payload.description

        if payload.status is not None:
            project.status = (
                payload.status.value if hasattr(payload.status, "value") else str(payload.status)
            )

        if payload.priority is not None:
            project.priority = (
                payload.priority.value if hasattr(payload.priority, "value") else str(payload.priority)
            )

        project.updated_at = datetime.now(timezone.utc)
        return self.project_repo.update(project)

    def delete_project(self, project_id: str) -> None:
        """Delete project by identifier or raise ResourceNotFoundError."""
        _ = self.get_project(project_id)
        self.project_repo.delete(project_id)
