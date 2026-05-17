"""
Basic test suite for the Task Manager API.
Run with:  pytest tests/ -v
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from backend.db.database import Base, get_db

# ── In-memory SQLite for tests ──
TEST_DATABASE_URL = "sqlite:///./test_taskmanager.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
Base.metadata.create_all(bind=engine)

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_db():
    """Drop and recreate all tables before each test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


# ── Helpers ──
def register_and_login(username="testuser", password="testpass123"):
    client.post("/register", json={"username": username, "email": f"{username}@example.com", "password": password})
    res = client.post("/login", json={"username": username, "password": password})
    return res.json()["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


# ── Auth tests ──
class TestAuth:
    def test_register_success(self):
        res = client.post("/register", json={
            "username": "alice", "email": "alice@example.com", "password": "secret123"
        })
        assert res.status_code == 201
        assert res.json()["username"] == "alice"

    def test_register_duplicate_username(self):
        client.post("/register", json={"username": "bob", "email": "bob@example.com", "password": "pass"})
        res = client.post("/register", json={"username": "bob", "email": "bob2@example.com", "password": "pass"})
        assert res.status_code == 400

    def test_login_success(self):
        client.post("/register", json={"username": "carol", "email": "carol@example.com", "password": "mypass"})
        res = client.post("/login", json={"username": "carol", "password": "mypass"})
        assert res.status_code == 200
        assert "access_token" in res.json()

    def test_login_wrong_password(self):
        client.post("/register", json={"username": "dave", "email": "dave@example.com", "password": "correct"})
        res = client.post("/login", json={"username": "dave", "password": "wrong"})
        assert res.status_code == 401


# ── Task tests ──
class TestTasks:
    def test_create_task(self):
        token = register_and_login()
        res = client.post("/tasks", json={"title": "Buy groceries"}, headers=auth_headers(token))
        assert res.status_code == 201
        assert res.json()["title"] == "Buy groceries"
        assert res.json()["completed"] is False

    def test_get_tasks(self):
        token = register_and_login()
        client.post("/tasks", json={"title": "Task 1"}, headers=auth_headers(token))
        client.post("/tasks", json={"title": "Task 2"}, headers=auth_headers(token))
        res = client.get("/tasks", headers=auth_headers(token))
        assert res.status_code == 200
        assert res.json()["total"] == 2

    def test_get_single_task(self):
        token = register_and_login()
        created = client.post("/tasks", json={"title": "Solo task"}, headers=auth_headers(token)).json()
        res = client.get(f"/tasks/{created['id']}", headers=auth_headers(token))
        assert res.status_code == 200
        assert res.json()["title"] == "Solo task"

    def test_complete_task(self):
        token = register_and_login()
        task = client.post("/tasks", json={"title": "Do laundry"}, headers=auth_headers(token)).json()
        res = client.put(f"/tasks/{task['id']}", json={"completed": True}, headers=auth_headers(token))
        assert res.status_code == 200
        assert res.json()["completed"] is True

    def test_delete_task(self):
        token = register_and_login()
        task = client.post("/tasks", json={"title": "Temp task"}, headers=auth_headers(token)).json()
        res = client.delete(f"/tasks/{task['id']}", headers=auth_headers(token))
        assert res.status_code == 204

    def test_cannot_access_other_users_task(self):
        token1 = register_and_login("user1", "pass1")
        token2 = register_and_login("user2", "pass2")
        task = client.post("/tasks", json={"title": "Private task"}, headers=auth_headers(token1)).json()
        res = client.get(f"/tasks/{task['id']}", headers=auth_headers(token2))
        assert res.status_code == 404

    def test_filter_by_completed(self):
        token = register_and_login()
        t1 = client.post("/tasks", json={"title": "Done"}, headers=auth_headers(token)).json()
        client.post("/tasks", json={"title": "Pending"}, headers=auth_headers(token))
        client.put(f"/tasks/{t1['id']}", json={"completed": True}, headers=auth_headers(token))

        done = client.get("/tasks?completed=true", headers=auth_headers(token)).json()
        pending = client.get("/tasks?completed=false", headers=auth_headers(token)).json()
        assert done["total"] == 1
        assert pending["total"] == 1

    def test_pagination(self):
        token = register_and_login()
        for i in range(15):
            client.post("/tasks", json={"title": f"Task {i}"}, headers=auth_headers(token))
        res = client.get("/tasks?page=1&page_size=10", headers=auth_headers(token)).json()
        assert res["total"] == 15
        assert len(res["tasks"]) == 10

    def test_unauthenticated_access(self):
        res = client.get("/tasks")
        assert res.status_code == 401
