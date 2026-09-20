"""Schemas package."""
from app.schemas.common import (
    DataResponse,
    ErrorBody,
    ErrorDetail,
    ErrorResponse,
    MessageData,
    MessageResponse,
    PaginatedResponse,
    PaginationMeta,
)
from app.schemas.project import (
    ProjectBase,
    ProjectCreate,
    ProjectPriority,
    ProjectResponse,
    ProjectStatus,
    ProjectUpdate,
)
from app.schemas.task import (
    TaskBase,
    TaskCreate,
    TaskPriority,
    TaskResponse,
    TaskStatus,
    TaskStatusUpdate,
    TaskUpdate,
)
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserResponse,
    UserRole,
    UserUpdate,
)

__all__ = [
    "DataResponse",
    "PaginatedResponse",
    "PaginationMeta",
    "ErrorDetail",
    "ErrorBody",
    "ErrorResponse",
    "MessageData",
    "MessageResponse",
    "UserRole",
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "ProjectStatus",
    "ProjectPriority",
    "ProjectBase",
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectResponse",
    "TaskStatus",
    "TaskPriority",
    "TaskBase",
    "TaskCreate",
    "TaskUpdate",
    "TaskStatusUpdate",
    "TaskResponse",
]
