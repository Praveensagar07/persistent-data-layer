"""User SQLAlchemy repository implementation."""

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User


class UserRepository:
    """Relational data access layer for User entities."""

    def __init__(self, db: Session = Depends(get_db)) -> None:
        self.db = db

    def get_by_id(self, user_id: str) -> User | None:
        """Find user by primary key ID."""
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        """Find user by case-insensitive unique email."""
        stmt = select(User).where(func.lower(User.email) == email.strip().lower())
        return self.db.execute(stmt).scalar_one_or_none()

    def list_users(
        self,
        skip: int = 0,
        limit: int = 20,
        role: str | None = None,
    ) -> tuple[list[User], int]:
        """List paginated users with optional role filtering."""
        base_query = select(User)
        count_query = select(func.count()).select_from(User)

        if role:
            target_role = role.strip().lower()
            base_query = base_query.where(func.lower(User.role) == target_role)
            count_query = count_query.where(func.lower(User.role) == target_role)

        total = self.db.execute(count_query).scalar_one()
        stmt = base_query.order_by(User.created_at.desc()).offset(skip).limit(limit)
        items = list(self.db.execute(stmt).scalars().all())
        return items, total

    def create(self, user: User) -> User:
        """Persist a newly created user."""
        self.db.add(user)
        self.db.flush()
        self.db.refresh(user)
        return user

    def update(self, user: User) -> User:
        """Persist modifications to an existing user."""
        self.db.flush()
        self.db.refresh(user)
        return user

    def delete(self, user_id: str) -> bool:
        """Delete user by ID."""
        user = self.get_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.flush()
            return True
        return False

    def count(self) -> int:
        """Total user count in database."""
        stmt = select(func.count()).select_from(User)
        return self.db.execute(stmt).scalar_one()
