"""Custom domain exceptions for centralized error handling."""

from typing import Any


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: list[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or []


class ResourceNotFoundError(AppException):
    """Raised when a requested resource is not found."""

    def __init__(
        self,
        message: str | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
    ) -> None:
        if message is None:
            if resource_type and resource_id:
                message = f"{resource_type} with id '{resource_id}' was not found"
            else:
                message = "Requested resource not found"
        super().__init__(
            message=message,
            code="RESOURCE_NOT_FOUND",
            status_code=404,
        )


class DuplicateResourceError(AppException):
    """Raised when an entity with duplicate unique identifier/field already exists."""

    def __init__(
        self,
        message: str = "Resource already exists",
        field: str | None = None,
        value: str | None = None,
    ) -> None:
        if field and value:
            message = f"Resource with {field} '{value}' already exists"
        super().__init__(
            message=message,
            code="DUPLICATE_RESOURCE",
            status_code=409,
        )


class InvalidOperationError(AppException):
    """Raised when a requested operation violates business invariants."""

    def __init__(
        self,
        message: str = "Invalid operation",
        details: list[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code="INVALID_OPERATION",
            status_code=400,
            details=details,
        )


class ValidationError(AppException):
    """Raised when custom business validation fails."""

    def __init__(
        self,
        message: str = "Validation failed",
        details: list[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=422,
            details=details,
        )
