"""SQLAlchemy declarative base for all Glimmer domain models."""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Root declarative base — all domain models inherit from this."""

    pass

