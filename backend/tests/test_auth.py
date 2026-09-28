import uuid


def test_patient_registration(client):
    unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"

    response = client.post(
        "/auth/register/patient",
        json={
            "name": "Test Patient",
            "email": unique_email,
            "password": "Test@12345",
            "date_of_birth": "2000-01-01",
            "gender": "male",
            "phone": "9876543210",
            "address": "Test Address",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["message"] == "Patient registered successfully."
    assert "user_id" in data
    assert "patient_id" in data


def test_patient_login(client):
    unique_email = f"login_{uuid.uuid4().hex[:8]}@example.com"
    password = "Test@12345"

    register_response = client.post(
        "/auth/register/patient",
        json={
            "name": "Login Test Patient",
            "email": unique_email,
            "password": password,
            "date_of_birth": "2000-01-01",
            "gender": "male",
            "phone": "9876543211",
            "address": "Test Address",
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "email": unique_email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    data = login_response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["account_type"] == "patient"