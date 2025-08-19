import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_register_user():
    """Prueba el registro de un nuevo usuario"""
    user_data = {
        "nombre_usuario": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "nombre": "Test",
        "apellido": "User",
        "fecha_nacimiento": "1990-01-01"
    }
    
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["nombre_usuario"] == "testuser"
    assert data["email"] == "test@example.com"

def test_login_user():
    """Prueba el login de un usuario"""
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data

def test_get_token():
    """Prueba obtener token JWT"""
    form_data = {
        "username": "test@example.com",
        "password": "testpassword123"
    }
    
    response = client.post("/auth/token", data=form_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data

def test_root_endpoint():
    """Prueba el endpoint raíz"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "mensaje" in data
    assert "version" in data
    assert "estado" in data 