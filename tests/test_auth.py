import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from app.main import app

client = TestClient(app)



def test_login_valid_credentials():
    mock_user = MagicMock()
    mock_user.id = "uuid-123"
    mock_user.email = "thiago@farmaos.com"

    mock_session = MagicMock()
    mock_session.access_token = "eyJtoken"

    mock_response = MagicMock()
    mock_response.user = mock_user
    mock_response.session = mock_session

    with patch("app.routers.auth.supabase") as mock_sb:
        mock_sb.auth.sign_in_with_password.return_value = mock_response

        response = client.post("/auth/login", json={
            "email": "thiago@farmaos.com",
            "password": "123456"
        })

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["email"] == "thiago@farmaos.com"



def test_login_invalid_credentials():
    with patch("app.routers.auth.supabase") as mock_sb:
        mock_sb.auth.sign_in_with_password.side_effect = Exception("Invalid credentials")

        response = client.post("/auth/login", json={
            "email": "thiago@farmaos.com",
            "password": "senhaerrada"
        })

    assert response.status_code == 401
    assert response.json()["detail"] == "Email ou senha inválidos"



def test_register_valid_data():
    mock_user = MagicMock()
    mock_user.id = "uuid-456"
    mock_user.email = "maria@farmaos.com"

    mock_response = MagicMock()
    mock_response.user = mock_user

    with patch("app.routers.auth.supabase") as mock_sb:
        mock_sb.auth.sign_up.return_value = mock_response

        response = client.post("/auth/register", json={
            "email": "maria@farmaos.com",
            "password": "senha123",
            "name": "Maria Silva",
            "role": "pharmacist"
        })

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "maria@farmaos.com"
    assert "user_id" in data


def test_register_duplicate_email():
    with patch("app.routers.auth.supabase") as mock_sb:
        mock_sb.auth.sign_up.side_effect = Exception("User already registered")

        response = client.post("/auth/register", json={
            "email": "thiago@farmaos.com",
            "password": "outrasenha",
            "name": "Outro Usuario",
            "role": "balconist"
        })

    assert response.status_code == 400


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert data["app"] == "FarmaOS"
    assert "version" in data
    assert "status" in data