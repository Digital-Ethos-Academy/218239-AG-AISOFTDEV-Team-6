import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app  # Your FastAPI instance
from database import Base, get_db  # Adjust: import your Base and get_db dependency

# --- Test data ---
ORG_DATA = {"name": "Test Org", "description": "A test organization"}
USER_DATA = {
    "email": "user@example.com",
    "name": "Alice",
}
MEETING_DATA = {
    "title": "Test Meeting",
    "organization_id": 1,
    "scheduled_start_time": "2025-07-31T10:00:00"  # Example ISO datetime
}

# --- Pytest fixture for isolated test database ---
@pytest.fixture
def client():
    # 1. Create an in-memory SQLite database
    TEST_DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # 2. Create all tables
    Base.metadata.create_all(bind=engine)

    # 3. Dependency override
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = override_get_db

    # 4. Provide test client
    with TestClient(app) as c:
        yield c

    # 5. Cleanup
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


# --- Root endpoint ---
def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "Meeting Intelligence Platform" in response.json()["message"]

# --- Organization CRUD ---
def test_create_organization(client):
    response = client.post("/organizations/", json=ORG_DATA)
    assert response.status_code == 201
    data = response.json()
    print(data)
    assert data["name"] == ORG_DATA["name"]
    assert "id" in data

def test_read_organizations(client):
    # Setup
    client.post("/organizations/", json=ORG_DATA)
    response = client.get("/organizations/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(org["name"] == ORG_DATA["name"] for org in data)

def test_read_organization_by_id(client):
    create_resp = client.post("/organizations/", json=ORG_DATA)
    org_id = create_resp.json()["id"]
    response = client.get(f"/organizations/{org_id}")
    assert response.status_code == 200
    assert response.json()["id"] == org_id

def test_update_organization(client):
    create_resp = client.post("/organizations/", json=ORG_DATA)
    org_id = create_resp.json()["id"]
    update_data = {"name": "Updated Org"}
    response = client.put(f"/organizations/{org_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Org"

def test_delete_organization(client):
    create_resp = client.post("/organizations/", json=ORG_DATA)
    org_id = create_resp.json()["id"]
    response = client.delete(f"/organizations/{org_id}")
    assert response.status_code == 204
    response = client.get(f"/organizations/{org_id}")
    assert response.status_code == 404

# --- User CRUD ---
def test_create_user(client):
    org_resp = client.post("/organizations/", json=ORG_DATA)
    org_id = org_resp.json()["id"]
    user = USER_DATA.copy()
    user["organization_id"] = org_id
    response = client.post("/users/", json=user)
    assert response.status_code == 201
    assert response.json()["email"] == USER_DATA["email"]

def test_read_users(client):
    response = client.get("/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_update_user(client):
    org_resp = client.post("/organizations/", json=ORG_DATA)
    org_id = org_resp.json()["id"]
    user = USER_DATA.copy()
    user["organization_id"] = org_id
    user_resp = client.post("/users/", json=user)
    user_id = user_resp.json()["id"]
    update_data = {"name": "Alice Updated"}
    response = client.put(f"/users/{user_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Alice Updated"

def test_delete_user(client):
    org_resp = client.post("/organizations/", json=ORG_DATA)
    org_id = org_resp.json()["id"]
    user = USER_DATA.copy()
    user["organization_id"] = org_id
    user_resp = client.post("/users/", json=user)
    user_id = user_resp.json()["id"]
    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 204

# --- Meeting CRUD ---
def test_create_meeting(client):
    org_resp = client.post("/organizations/", json=ORG_DATA)
    org_id = org_resp.json()["id"]
    meeting = MEETING_DATA.copy()
    meeting["organization_id"] = org_id
    response = client.post("/meetings/", json=meeting)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == MEETING_DATA["title"]
    assert data["organization_id"] == org_id

def test_read_meetings(client):
    response = client.get("/meetings/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_update_meeting(client):
    org_resp = client.post("/organizations/", json=ORG_DATA)
    org_id = org_resp.json()["id"]
    meeting = MEETING_DATA.copy()
    meeting["organization_id"] = org_id
    meet_resp = client.post("/meetings/", json=meeting)
    meeting_id = meet_resp.json()["id"]
    update_data = {"title": "Updated Meeting"}
    response = client.put(f"/meetings/{meeting_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Meeting"

def test_delete_meeting(client):
    org_resp = client.post("/organizations/", json=ORG_DATA)
    org_id = org_resp.json()["id"]
    meeting = MEETING_DATA.copy()
    meeting["organization_id"] = org_id
    meet_resp = client.post("/meetings/", json=meeting)
    meeting_id = meet_resp.json()["id"]
    response = client.delete(f"/meetings/{meeting_id}")
    assert response.status_code == 204