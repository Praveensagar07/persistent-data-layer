"""Project schemas and request/response models."""

from datetime import datetime
from enum import Enum
from pydantic import Field, field_validator
from app.schemas.common import BaseSchema


class ProjectStatus(str, Enum):
    """Lifecycle status of a project."""

    PLANNING = "planning"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ProjectPriority(str, Enum):
    """Project priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ProjectBase(BaseSchema):
    """Base fields shared by project schemas."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=120,
        description="Name of the project",
        examples=["Developer Productivity Dashboard"],
    )
    description: str | None = Field(
        None,
        max_length=1000,
        description="Optional detailed project overview",
        examples=["A unified metrics and task tracking platform for development teams."],
    )
    status: ProjectStatus = Field(
        default=ProjectStatus.PLANNING,
        description="Current project lifecycle status",
        examples=[ProjectStatus.ACTIVE],
    )
    priority: ProjectPriority = Field(
        default=ProjectPriority.MEDIUM,
        description="Strategic priority level",
        examples=[ProjectPriority.HIGH],
    )
    owner_id: str = Field(
        ...,
        min_length=1,
        description="User ID of the project owner",
        examples=["usr_9a8b7c6d5e4f"],
    )

    @field_validator("name")
    @classmethod
    def validate_name_not_blank(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Project name must not be empty or blank whitespace")
        return trimmed

    @field_validator("owner_id")
    @classmethod
    def validate_owner_id_not_blank(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("owner_id must not be empty or blank whitespace")
        return trimmed


class ProjectCreate(ProjectBase):
    """Payload for creating a new project."""

    pass


class ProjectUpdate(BaseSchema):
    """Payload for updating an existing project."""

    name: str | None = Field(
        None,
        min_length=1,
        max_length=120,
        description="Updated project name",
        examples=["Developer Productivity Platform v2"],
    )
    description: str | None = Field(
        None,
        max_length=1000,
        description="Updated project description",
    )
    status: ProjectStatus | None = Field(
        None,
        description="Updated project status",
        examples=[ProjectStatus.COMPLETED],
    )
    priority: ProjectPriority | None = Field(
        None,
        description="Updated project priority",
        examples=[ProjectPriority.CRITICAL],
    )
    owner_id: str | None = Field(
        None,
        min_length=1,
        description="Updated owner ID (must be a valid user)",
    )

    @field_validator("name")
    @classmethod
    def validate_name_if_present(cls, v: str | None) -> str | None:
        if v is not None:
            trimmed = v.strip()
            if not trimmed:
                raise ValueError("Project name cannot be empty or blank whitespace")
            return trimmed
        return v

    @field_validator("owner_id")
    @classmethod
    def validate_owner_id_if_present(cls, v: str | None) -> str | None:
        if v is not None:
            trimmed = v.strip()
            if not trimmed:
                raise ValueError("owner_id cannot be empty or blank whitespace")
            return trimmed
        return v


class ProjectResponse(BaseSchema):
    """Schema returned for project data."""

    id: str = Field(..., description="Unique project identifier", examples=["prj_1a2b3c4d5e6f"])
    name: str = Field(..., description="Project name", examples=["Developer Productivity Dashboard"])
    description: str | None = Field(None, description="Project description")
    status: str = Field(..., description="Current status", examples=["active"])
    priority: str = Field(..., description="Priority level", examples=["high"])
    owner_id: str = Field(..., description="User ID of the project owner", examples=["usr_9a8b7c6d5e4f"])
    created_at: datetime = Field(..., description="Creation timestamp in UTC")
    updated_at: datetime = Field(..., description="Last update timestamp in UTC")
