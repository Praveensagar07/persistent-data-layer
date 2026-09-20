"""Common reusable schemas and response envelopes."""

from typing import Any, Generic, TypeVar
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class BaseSchema(BaseModel):
    """Base schema with standard model configuration."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class DataResponse(BaseModel, Generic[T]):
    """Standard success wrapper for a single data payload."""

    data: T


class PaginationMeta(BaseModel):
    """Metadata describing paginated result sets."""

    total: int = Field(..., description="Total count of matching items", ge=0, examples=[42])
    skip: int = Field(..., description="Number of items skipped", ge=0, examples=[0])
    limit: int = Field(..., description="Maximum items requested per page", ge=1, le=100, examples=[20])


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard success wrapper for paginated collections."""

    data: list[T]
    meta: PaginationMeta


class ErrorDetail(BaseModel):
    """Detailed information for specific validation errors."""

    field: str = Field(..., description="Path to the invalid field", examples=["body.email"])
    message: str = Field(..., description="Descriptive error explanation", examples=["value is not a valid email address"])
    type: str = Field(..., description="Error category classification", examples=["value_error"])


class ErrorBody(BaseModel):
    """Standard error payload content."""

    code: str = Field(..., description="Machine-readable error code", examples=["RESOURCE_NOT_FOUND"])
    message: str = Field(..., description="Human-readable error summary", examples=["Task with id 'tsk_123' was not found"])
    details: list[dict[str, Any]] = Field(default_factory=list, description="Specific field-level details if available")


class ErrorResponse(BaseModel):
    """Global standardized API error response envelope."""

    error: ErrorBody


class MessageData(BaseModel):
    """General action confirmation payload."""

    message: str = Field(..., description="Status message", examples=["Resource deleted successfully"])
    id: str | None = Field(None, description="Impacted resource ID", examples=["usr_1a2b3c4d"])


class MessageResponse(BaseModel):
    """Confirmation response wrapper."""

    data: MessageData
