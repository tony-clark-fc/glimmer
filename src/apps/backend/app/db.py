"""Glimmer backend — database engine and session wiring.

Provides the async-compatible SQLAlchemy engine and a session factory.
Uses the synchronous psycopg driver by default for local-first simplicity;
the engine is created lazily on first use.
"""

from __future__ import annotations

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings

_engine: Engine | None = None


def get_engine() -> Engine:
    """Return the (lazily-created) SQLAlchemy engine."""
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_engine(
            settings.database_url,
            echo=settings.debug,
            pool_pre_ping=True,
        )
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    """Return a sessionmaker bound to the current engine."""
    return sessionmaker(bind=get_engine(), expire_on_commit=False)


def get_session() -> Session:
    """Convenience: open a new session from the default factory."""
    return get_session_factory()()

