import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app, get_db
from app.models import Base

TEST_DB_URL = "sqlite+pysqlite:///:memory:"

# Test engine
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Create tables once per test session
Base.metadata.create_all(bind=engine)

@pytest.fixture
def db_session():
    """Provides a database session for each test."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def client(db_session):
    """Provides a FastAPI test client with DB override."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    # override dependency
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    # cleanup overrides
    app.dependency_overrides.clear()
