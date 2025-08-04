import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_account_get():
    response = client.get("/create_account")
    assert response.status_code == 200
    assert "Sign Up" in response.text or "Create Account" in response.text

def test_create_account_post(monkeypatch):
    async def dummy_register_user(db, reg):
        return None
    monkeypatch.setattr("app.auth.dependency.register_user", dummy_register_user)
    data = {
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User",
        "email": "testuser@example.com",
        "password": "testpass123"
    }
    response = client.post("/create_account", data=data)
    assert response.status_code == 200
    assert "Account created successfully" in response.text or "Sign Up" in response.text
