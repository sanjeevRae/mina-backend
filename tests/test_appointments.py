import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient


def create_authenticated_user(client: TestClient, user_data):
    """Helper function to create and authenticate a user"""
    # Register user
    client.post("/api/v1/auth/register", json=user_data)
    
    # Login
    login_response = client.post("/api/v1/auth/login", json={
        "username": user_data["username"],
        "password": user_data["password"]
    })
    
    token = login_response.json()["access_token"]
    user_response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    user_id = user_response.json()["id"]
    
    return token, user_id


def test_create_appointment(client: TestClient, sample_user_data, sample_doctor_data):
    """Test creating an appointment"""
    # Create patient and doctor
    patient_token, patient_id = create_authenticated_user(client, sample_user_data)
    doctor_token, doctor_id = create_authenticated_user(client, sample_doctor_data)
    
    # Create appointment
    appointment_data = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "scheduled_at": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "title": "Test Consultation",
        "description": "Test appointment",
        "appointment_type": "video_call",
        "symptoms": ["headache", "fever"]
    }
    
    headers = {"Authorization": f"Bearer {patient_token}"}
    response = client.post("/api/v1/appointments/", json=appointment_data, headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == appointment_data["title"]
    assert data["patient_id"] == patient_id
    assert data["doctor_id"] == doctor_id


def test_list_appointments(client: TestClient, sample_user_data, sample_doctor_data):
    """Test listing appointments"""
    # Create patient and doctor
    patient_token, patient_id = create_authenticated_user(client, sample_user_data)
    doctor_token, doctor_id = create_authenticated_user(client, sample_doctor_data)
    
    # Create appointment
    appointment_data = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "scheduled_at": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "title": "Test Consultation",
        "appointment_type": "video_call"
    }
    
    patient_headers = {"Authorization": f"Bearer {patient_token}"}
    client.post("/api/v1/appointments/", json=appointment_data, headers=patient_headers)
    
    # List appointments as patient
    response = client.get("/api/v1/appointments/", headers=patient_headers)
    assert response.status_code == 200
    
    appointments = response.json()
    assert len(appointments) == 1
    assert appointments[0]["title"] == appointment_data["title"]


def test_unauthorized_appointment_access(client: TestClient, sample_user_data, sample_doctor_data):
    """Test that users cannot access other users' appointments"""
    # Create two patients
    patient1_data = sample_user_data.copy()
    patient2_data = sample_user_data.copy()
    patient2_data["email"] = "patient2@example.com"
    patient2_data["username"] = "patient2"
    
    patient1_token, patient1_id = create_authenticated_user(client, patient1_data)
    patient2_token, patient2_id = create_authenticated_user(client, patient2_data)
    doctor_token, doctor_id = create_authenticated_user(client, sample_doctor_data)
    
    # Create appointment for patient1
    appointment_data = {
        "patient_id": patient1_id,
        "doctor_id": doctor_id,
        "scheduled_at": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "title": "Private Consultation",
        "appointment_type": "video_call"
    }
    
    patient1_headers = {"Authorization": f"Bearer {patient1_token}"}
    response = client.post("/api/v1/appointments/", json=appointment_data, headers=patient1_headers)
    appointment_id = response.json()["id"]
    
    # Try to access appointment as patient2
    patient2_headers = {"Authorization": f"Bearer {patient2_token}"}
    response = client.get(f"/api/v1/appointments/{appointment_id}", headers=patient2_headers)
    assert response.status_code == 403


def test_appointment_status_update(client: TestClient, sample_user_data, sample_doctor_data):
    """Test updating appointment status"""
    # Create patient and doctor
    patient_token, patient_id = create_authenticated_user(client, sample_user_data)
    doctor_token, doctor_id = create_authenticated_user(client, sample_doctor_data)
    
    # Create appointment
    appointment_data = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "scheduled_at": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "title": "Test Consultation",
        "appointment_type": "video_call"
    }
    
    patient_headers = {"Authorization": f"Bearer {patient_token}"}
    response = client.post("/api/v1/appointments/", json=appointment_data, headers=patient_headers)
    appointment_id = response.json()["id"]
    
    # Update status as doctor
    doctor_headers = {"Authorization": f"Bearer {doctor_token}"}
    status_update = {"status": "confirmed"}
    
    response = client.patch(
        f"/api/v1/appointments/{appointment_id}/status",
        json=status_update,
        headers=doctor_headers
    )
    
    assert response.status_code == 200
    assert response.json()["status"] == "confirmed"