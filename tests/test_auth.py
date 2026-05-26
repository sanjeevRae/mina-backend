import pytest
from fastapi.testclient import TestClient

from app.services.file_service import file_storage_service


def _login_headers(client: TestClient, sample_user_data: dict) -> dict:
    client.post("/api/v1/auth/register", json=sample_user_data)
    login_response = client.post("/api/v1/auth/login", json={
        "username": sample_user_data["username"],
        "password": sample_user_data["password"]
    })
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


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


def test_upload_profile_image_updates_current_user(
    client: TestClient,
    sample_user_data,
    monkeypatch
):
    """Test uploading a profile image updates the current user record."""
    headers = _login_headers(client, sample_user_data)
    captured = {}

    async def fake_upload_file(file_content, filename, folder="medical_files", user_id=None, prefer_cloudinary=False):
        captured["filename"] = filename
        captured["folder"] = folder
        captured["user_id"] = user_id
        captured["prefer_cloudinary"] = prefer_cloudinary
        captured["size"] = len(file_content)
        return {
            "success": True,
            "filename": filename,
            "url": "https://res.cloudinary.com/demo/image/upload/v123/profile_images/patient/1/avatar_123.png",
            "storage_type": "cloudinary",
            "public_id": "profile_images/patient/1/avatar_123",
            "size": len(file_content)
        }

    monkeypatch.setattr(file_storage_service, "upload_file", fake_upload_file)

    response = client.post(
        "/api/v1/auth/me/profile-image",
        headers=headers,
        files={"file": ("avatar.png", b"\x89PNG\r\n\x1a\nfake-image-bytes", "image/png")}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["profile_image_url"] == "https://res.cloudinary.com/demo/image/upload/v123/profile_images/patient/1/avatar_123.png"
    assert captured["filename"] == "avatar.png"
    assert captured["folder"] == "profile_images/patient"
    assert captured["prefer_cloudinary"] is True
    assert captured["user_id"] == data["id"]

    me_response = client.get("/api/v1/auth/me", headers=headers)
    assert me_response.status_code == 200
    assert me_response.json()["profile_image_url"] == data["profile_image_url"]


def test_upload_profile_image_rejects_non_image(client: TestClient, sample_user_data):
    """Test profile image uploads reject unsupported file types."""
    headers = _login_headers(client, sample_user_data)

    response = client.post(
        "/api/v1/auth/me/profile-image",
        headers=headers,
        files={"file": ("report.pdf", b"%PDF-1.4 fake pdf", "application/pdf")}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Only JPG, JPEG, and PNG files can be used as profile images"


def test_document_upload_prefers_cloudinary(client: TestClient, sample_user_data, monkeypatch):
    """Test document uploads request Cloudinary-preferred storage."""
    headers = _login_headers(client, sample_user_data)
    captured = {}

    async def fake_upload_file(file_content, filename, folder="medical_files", user_id=None, prefer_cloudinary=False):
        captured["filename"] = filename
        captured["folder"] = folder
        captured["user_id"] = user_id
        captured["prefer_cloudinary"] = prefer_cloudinary
        return {
            "success": True,
            "filename": filename,
            "url": "https://res.cloudinary.com/demo/raw/upload/v123/medical_files/1/report_123.pdf",
            "storage_type": "cloudinary",
            "public_id": "medical_files/1/report_123",
            "size": len(file_content)
        }

    monkeypatch.setattr(file_storage_service, "upload_file", fake_upload_file)

    response = client.post(
        "/api/v1/documents/upload",
        headers=headers,
        data={"folder": "medical_files", "description": "Lab report"},
        files={"file": ("report.pdf", b"%PDF-1.4 fake pdf bytes", "application/pdf")}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["file"]["storage_type"] == "cloudinary"
    assert data["file"]["public_id"] == "medical_files/1/report_123"
    assert captured["filename"] == "report.pdf"
    assert captured["folder"] == "medical_files"
    assert captured["prefer_cloudinary"] is True
