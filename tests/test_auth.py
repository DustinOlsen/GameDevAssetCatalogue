import pytest


def test_register_success(client):
    """Test successful user registration"""
    response = client.post(
        "/api/auth/register",
        json={"username": "newuser", "password": "securepass123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "User created successfully"


def test_register_duplicate_username(client, test_user):
    """Test registration with existing username fails"""
    response = client.post(
        "/api/auth/register",
        json={"username": test_user["username"], "password": "anotherpass"}
    )
    assert response.status_code == 400
    # Updated to match actual error message
    assert "already taken" in response.json()["detail"].lower()


def test_login_success(client, test_user):
    """Test successful login returns token"""
    response = client.post(
        "/api/auth/login",
        json={"username": test_user["username"], "password": test_user["password"]}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, test_user):
    """Test login with wrong password fails"""
    response = client.post(
        "/api/auth/login",
        json={"username": test_user["username"], "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]


def test_login_nonexistent_user(client):
    """Test login with nonexistent user fails"""
    response = client.post(
        "/api/auth/login",
        json={"username": "doesnotexist", "password": "somepass"}
    )
    assert response.status_code == 401


def test_protected_endpoint_without_token(client):
    """Test accessing protected endpoint without token fails"""
    response = client.get("/api/assets")
    assert response.status_code == 403


def test_protected_endpoint_with_invalid_token(client):
    """Test accessing protected endpoint with invalid token fails"""
    response = client.get(
        "/api/assets",
        headers={"Authorization": "Bearer invalid_token_here"}
    )
    assert response.status_code == 401