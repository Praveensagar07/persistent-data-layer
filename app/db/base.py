"""SQLAlchemy declarative base and entity registrations."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy relational domain models."""
    pass
