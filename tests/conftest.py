# conftest.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from validation_models.sql_models import Base  # Adjust import if needed

# --- 1. Create a test engine and sessionmaker for in-memory SQLite ---
SQLALCHEMY_DATABASE_URL = "sqlite://"

# For in-memory SQLite, use StaticPool and connect_args
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- 2. Create and override the get_db dependency ---
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides = {}  # Clear any existing overrides
app.dependency_overrides['get_db'] = override_get_db

# --- 3. Fixture to set up/teardown test database ---
@pytest.fixture(scope="function")
def db_session():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Clean up the DB after each test
        Base.metadata.drop_all(bind=engine)

# --- 4. Fixture for test client (uses dependency override for DB) ---
@pytest.fixture(scope="function")
def client(db_session):
    # You can use FastAPI's TestClient for sync tests
    with TestClient(app) as c:
        yield c

# --- 5. Optionally, provide a fixture for direct DB access in tests ---
@pytest.fixture(scope="function")
def session(db_session):
    # Alias for clarity - use this in your tests for direct DB access
    yield db_session