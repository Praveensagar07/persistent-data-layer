"""User business service layer."""

from datetime import datetime, timezone
from fastapi import Depends
from app.core.exceptions import DuplicateResourceError, ResourceNotFoundError
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate
from app.utils.ids import generate_id


class UserService:
    """Business logic orchestrator for User operations."""

    def __init__(self, user_repo: UserRepository = Depends()) -> None:
        self.user_repo = user_repo

    def create_user(self, payload: UserCreate) -> User:
        """Create a new user ensuring unique email invariant."""
        normalized_email = payload.email.strip().lower()
        existing = self.user_repo.get_by_email(normalized_email)
        if existing:
            raise DuplicateResourceError(
                field="email",
                value=payload.email,
                message=f"A user with email '{payload.email}' already exists",
            )

        now = datetime.now(timezone.utc)
        user = User(
            id=generate_id("usr"),
            name=payload.name,
            email=normalized_email,
            role=payload.role.value if hasattr(payload.role, "value") else str(payload.role),
            created_at=now,
            updated_at=now,
        )
        return self.user_repo.create(user)

    def get_user(self, user_id: str) -> User:
        """Fetch user by identifier or raise ResourceNotFoundError."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundError(resource_type="User", resource_id=user_id)
        return user

    def list_users(
        self,
        skip: int = 0,
        limit: int = 20,
        role: str | None = None,
    ) -> tuple[list[User], int]:
        """List paginated users with optional role filter."""
        return self.user_repo.list_users(skip=skip, limit=limit, role=role)

    def update_user(self, user_id: str, payload: UserUpdate) -> User:
        """Update existing user fields with duplicate email validation."""
        user = self.get_user(user_id)

        if payload.email is not None:
            normalized_email = payload.email.strip().lower()
            if normalized_email != user.email.lower():
                existing = self.user_repo.get_by_email(normalized_email)
                if existing and existing.id != user.id:
                    raise DuplicateResourceError(
                        field="email",
                        value=payload.email,
                        message=f"A user with email '{payload.email}' already exists",
                    )
                user.email = normalized_email

        if payload.name is not None:
            user.name = payload.name

        if payload.role is not None:
            user.role = (
                payload.role.value if hasattr(payload.role, "value") else str(payload.role)
            )

        user.updated_at = datetime.now(timezone.utc)
        return self.user_repo.update(user)

    def delete_user(self, user_id: str) -> None:
        """Delete user by identifier or raise ResourceNotFoundError."""
        _ = self.get_user(user_id)
        self.user_repo.delete(user_id)
