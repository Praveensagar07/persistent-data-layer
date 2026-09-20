"""Task schemas and request/response models."""

from datetime import datetime
from enum import Enum
from pydantic import Field, field_validator
from app.schemas.common import BaseSchema


class TaskStatus(str, Enum):
    """Task progress state."""

    TODO = "todo"
    IN_PROGRESS = "in-progress"
    DONE = "done"


class TaskPriority(str, Enum):
    """Task urgency level."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskBase(BaseSchema):
    """Base fields shared by task schemas."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=150,
        description="Concise title describing the work item",
        examples=["Implement centralized error handlers"],
    )
    description: str | None = Field(
        None,
        max_length=2000,
        description="Detailed specification or acceptance criteria",
        examples=["Trap AppException, validation errors, and uncaught exceptions with standard envelopes."],
    )
    project_id: str = Field(
        ...,
        min_length=1,
        description="ID of the parent project",
        examples=["prj_1a2b3c4d5e6f"],
    )
    assignee_id: str | None = Field(
        None,
        description="User ID of the assigned team member",
        examples=["usr_9a8b7c6d5e4f"],
    )
    status: TaskStatus = Field(
        default=TaskStatus.TODO,
        description="Current task status (todo, in-progress, done)",
        examples=[TaskStatus.IN_PROGRESS],
    )
    priority: TaskPriority = Field(
        default=TaskPriority.MEDIUM,
        description="Task priority level (low, medium, high, critical)",
        examples=[TaskPriority.HIGH],
    )
    due_date: datetime | None = Field(
        None,
        description="Optional ISO timestamp deadline",
    )

    @field_validator("title")
    @classmethod
    def validate_title_not_blank(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Task title must not be empty or blank whitespace")
        return trimmed

    @field_validator("project_id")
    @classmethod
    def validate_project_id_not_blank(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("project_id must not be empty or blank whitespace")
        return trimmed

    @field_validator("assignee_id")
    @classmethod
    def validate_assignee_id(cls, v: str | None) -> str | None:
        if v is not None:
            trimmed = v.strip()
            return trimmed if trimmed else None
        return None


class TaskCreate(TaskBase):
    """Payload for creating a new task."""

    pass


class TaskUpdate(BaseSchema):
    """Payload for updating an existing task."""

    title: str | None = Field(
        None,
        min_length=1,
        max_length=150,
        description="Updated task title",
    )
    description: str | None = Field(
        None,
        max_length=2000,
        description="Updated task description",
    )
    project_id: str | None = Field(
        None,
        min_length=1,
        description="Move task to a different project",
    )
    assignee_id: str | None = Field(
        None,
        description="Reassign task to a different user, or empty string to unassign",
    )
    status: TaskStatus | None = Field(
        None,
        description="Updated task status",
    )
    priority: TaskPriority | None = Field(
        None,
        description="Updated task priority",
    )
    due_date: datetime | None = Field(
        None,
        description="Updated ISO timestamp deadline",
    )

    @field_validator("title")
    @classmethod
    def validate_title_if_present(cls, v: str | None) -> str | None:
        if v is not None:
            trimmed = v.strip()
            if not trimmed:
                raise ValueError("Task title cannot be empty or blank whitespace")
            return trimmed
        return v

    @field_validator("project_id")
    @classmethod
    def validate_project_id_if_present(cls, v: str | None) -> str | None:
        if v is not None:
            trimmed = v.strip()
            if not trimmed:
                raise ValueError("project_id cannot be empty or blank whitespace")
            return trimmed
        return v


class TaskStatusUpdate(BaseSchema):
    """Payload for updating only the task status."""

    status: TaskStatus = Field(
        ...,
        description="New task status (must be one of: todo, in-progress, done)",
        examples=[TaskStatus.IN_PROGRESS],
    )


class TaskResponse(BaseSchema):
    """Schema returned for task data."""

    id: str = Field(..., description="Unique task identifier", examples=["tsk_7a6b5c4d3e2f"])
    title: str = Field(..., description="Task title", examples=["Implement centralized error handlers"])
    description: str | None = Field(None, description="Task detailed description")
    project_id: str = Field(..., description="Parent project identifier", examples=["prj_1a2b3c4d5e6f"])
    assignee_id: str | None = Field(None, description="Assigned user identifier", examples=["usr_9a8b7c6d5e4f"])
    status: str = Field(..., description="Current status", examples=["in-progress"])
    priority: str = Field(..., description="Priority level", examples=["high"])
    due_date: datetime | None = Field(None, description="Due date timestamp")
    created_at: datetime = Field(..., description="Creation timestamp in UTC")
    updated_at: datetime = Field(..., description="Last update timestamp in UTC")
