import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app

# A separate, disposable SQLite file just for tests — never touches
# your real local.db, so test runs can't corrupt your dev data, and
# a fresh schema is created every run (avoiding the exact stale-schema
# bug we hit earlier).
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Replaces the real get_db() dependency during tests, so routes
    use the test database instead of local.db."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function", autouse=True)
def reset_database():
    """Runs automatically before EVERY test (autouse=True): drops and
    recreates all tables, so each test starts from a clean, empty
    database. This is what keeps tests independent of each other —
    a product created in one test won't leak into the next."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Provides a TestClient any test can use to make requests against
    your actual FastAPI app, e.g. client.get('/api/v1/products')."""
    return TestClient(app)