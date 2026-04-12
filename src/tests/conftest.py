"""Root conftest — shared fixtures for the Glimmer test suite.

Provides a configured test client and isolated test database session.
"""

from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config import get_settings
from app.main import create_app
from app.models import Base


@pytest.fixture(scope="session")
def test_engine():
    """Create a SQLAlchemy engine pointed at the test database."""
    settings = get_settings()
    engine = create_engine(settings.test_database_url, echo=False)
    # Ensure tables exist in the test database
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture()
def db_session(test_engine) -> Generator[Session, None, None]:
    """Provide a transactional database session that rolls back after each test."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    """Provide a FastAPI TestClient against a fresh app instance."""
    app = create_app()
    with TestClient(app) as c:
        yield c




