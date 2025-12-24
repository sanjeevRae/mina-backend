import pytest
from fastapi.testclient import TestClient


def test_user_registration(client: TestClient, sample_user_data):
    """Test user registration"""
    response = client.post("/api/v1/auth/register", json=sample_user_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["email"] == sample_user_data["email"]
    assert data["username"] == sample_user_data["username"]
    assert data["full_name"] == sample_user_data["full_name"]
    assert "id" in data


def test_user_login(client: TestClient, sample_user_data):
    """Test user login"""
    # First register the user
    client.post("/api/v1/auth/register", json=sample_user_data)
    
    # Then login
    login_data = {
        "username": sample_user_data["username"],
        "password": sample_user_data["password"]
    }
    
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_get_current_user(client: TestClient, sample_user_data):
    """Test getting current user profile"""
    # Register and login
    client.post("/api/v1/auth/register", json=sample_user_data)
    
    login_response = client.post("/api/v1/auth/login", json={
        "username": sample_user_data["username"],
        "password": sample_user_data["password"]
    })
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get current user
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["email"] == sample_user_data["email"]


def test_invalid_login(client: TestClient):
    """Test login with invalid credentials"""
    login_data = {
        "username": "nonexistent",
        "password": "wrongpassword"
    }
    
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 401


def test_duplicate_registration(client: TestClient, sample_user_data):
    """Test registration with duplicate email"""
    # Register user first time
    client.post("/api/v1/auth/register", json=sample_user_data)
    
    # Try to register again
    response = client.post("/api/v1/auth/register", json=sample_user_data)
    assert response.status_code == 400