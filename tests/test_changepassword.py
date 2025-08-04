import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_changepassword_get():
    response = client.get("/changepassword")
    assert response.status_code == 200
    assert "Change Password" in response.text

def test_changepassword_post_not_logged_in():
    response = client.post("/changepassword", data={
        "current_password": "oldpass",
        "new_password": "newpass",
        "new_password_confirm": "newpass"
    })
    # Should fail because not logged in
    assert response.status_code == 200
    assert "Failed" in response.text or "could not validate credentials" in response.text.lower()
