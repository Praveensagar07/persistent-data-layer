"""Project SQLAlchemy repository implementation."""

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.project import Project


class ProjectRepository:
    """Relational data access layer for Project entities."""

    def __init__(self, db: Session = Depends(get_db)) -> None:
        self.db = db

    def get_by_id(self, project_id: str) -> Project | None:
        """Find project by primary key ID."""
        return self.db.get(Project, project_id)

    def list_projects(
        self,
        skip: int = 0,
        limit: int = 20,
        owner_id: str | None = None,
        status: str | None = None,
    ) -> tuple[list[Project], int]:
        """List paginated projects with optional owner/status filters."""
        base_query = select(Project)
        count_query = select(func.count()).select_from(Project)

        if owner_id:
            base_query = base_query.where(Project.owner_id == owner_id.strip())
            count_query = count_query.where(Project.owner_id == owner_id.strip())

        if status:
            target_status = status.strip().lower()
            base_query = base_query.where(func.lower(Project.status) == target_status)
            count_query = count_query.where(func.lower(Project.status) == target_status)

        total = self.db.execute(count_query).scalar_one()
        stmt = base_query.order_by(Project.created_at.desc()).offset(skip).limit(limit)
        items = list(self.db.execute(stmt).scalars().all())
        return items, total

    def create(self, project: Project) -> Project:
        """Persist a newly created project."""
        self.db.add(project)
        self.db.flush()
        self.db.refresh(project)
        return project

    def update(self, project: Project) -> Project:
        """Persist modifications to an existing project."""
        self.db.flush()
        self.db.refresh(project)
        return project

    def delete(self, project_id: str) -> bool:
        """Delete project by ID (cascades to tasks)."""
        project = self.get_by_id(project_id)
        if project:
            self.db.delete(project)
            self.db.flush()
            return True
        return False

    def count(self) -> int:
        """Total project count in database."""
        stmt = select(func.count()).select_from(Project)
        return self.db.execute(stmt).scalar_one()
