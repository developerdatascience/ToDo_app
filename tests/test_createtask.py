import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/tasks/")
    assert response.status_code == 200
    assert "base" in response.text.lower()

def test_goto_todos():
    response = client.get("/tasks/add-todos")
    assert response.status_code == 200
    assert "addtask" in response.text.lower()

def test_add_task_redirect(monkeypatch):
    class DummyTask:
        pass
    async def dummy_create_task(db, task):
        return DummyTask()
    monkeypatch.setattr("app.crud.create_task", dummy_create_task)
    data = {
        "title": "Test Task",
        "description": "Test Desc",
        "priority": "High",
        "repeat": "None",
        "calendar": "2025-08-01"
    }
    response = client.post("/tasks/add-task", data=data, allow_redirects=False)
    assert response.status_code == 303
    assert "/tasks/add-todos" in response.headers["location"]
