"""User schemas and request/response models."""

import re
from datetime import datetime
from enum import Enum
from pydantic import Field, field_validator
from app.schemas.common import BaseSchema

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


class UserRole(str, Enum):
    """User organizational roles."""

    ADMIN = "admin"
    DEVELOPER = "developer"
    DESIGNER = "designer"
    PRODUCT_MANAGER = "product_manager"
    QA_ENGINEER = "qa_engineer"
    LEAD_ARCHITECT = "lead_architect"


class UserBase(BaseSchema):
    """Base fields for user payloads."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Full name of the user",
        examples=["Sarah Connor"],
    )
    email: str = Field(
        ...,
        min_length=5,
        max_length=120,
        description="Unique email address",
        examples=["sarah.connor@example.com"],
    )
    role: UserRole = Field(
        default=UserRole.DEVELOPER,
        description="Assigned organizational role",
        examples=[UserRole.DEVELOPER],
    )

    @field_validator("name")
    @classmethod
    def validate_name_not_blank(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Name must not be empty or blank whitespace")
        return trimmed

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        trimmed = v.strip().lower()
        if not EMAIL_REGEX.match(trimmed):
            raise ValueError("Email must be a valid email address (e.g., user@example.com)")
        return trimmed


class UserCreate(UserBase):
    """Payload for creating a new user."""

    pass


class UserUpdate(BaseSchema):
    """Payload for updating an existing user."""

    name: str | None = Field(
        None,
        min_length=1,
        max_length=100,
        description="Updated full name",
        examples=["Sarah Connor-Reese"],
    )
    email: str | None = Field(
        None,
        min_length=5,
        max_length=120,
        description="Updated unique email",
        examples=["sarah.reese@example.com"],
    )
    role: UserRole | None = Field(
        None,
        description="Updated role",
        examples=[UserRole.LEAD_ARCHITECT],
    )

    @field_validator("name")
    @classmethod
    def validate_name_if_present(cls, v: str | None) -> str | None:
        if v is not None:
            trimmed = v.strip()
            if not trimmed:
                raise ValueError("Name cannot be empty or blank whitespace")
            return trimmed
        return v

    @field_validator("email")
    @classmethod
    def validate_email_if_present(cls, v: str | None) -> str | None:
        if v is not None:
            trimmed = v.strip().lower()
            if not EMAIL_REGEX.match(trimmed):
                raise ValueError("Email must be a valid email address (e.g., user@example.com)")
            return trimmed
        return v


class UserResponse(BaseSchema):
    """Schema returned for user data."""

    id: str = Field(..., description="Unique user identifier", examples=["usr_9a8b7c6d5e4f"])
    name: str = Field(..., description="Full user name", examples=["Sarah Connor"])
    email: str = Field(..., description="Unique email address", examples=["sarah.connor@example.com"])
    role: str = Field(..., description="Assigned role", examples=["developer"])
    created_at: datetime = Field(..., description="Creation timestamp in UTC")
    updated_at: datetime = Field(..., description="Last update timestamp in UTC")
