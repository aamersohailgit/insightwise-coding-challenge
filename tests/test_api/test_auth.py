import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def user_data():
    """Return test user data."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }

@pytest.fixture
def registered_user(client, user_data):
    """Register a test user and return the response data."""
    response = client.post("/api/v1/auth/register", json=user_data)
    return response.json()

@pytest.fixture
def auth_token(client, user_data):
    """Get an auth token for the test user."""
    # Register the user first
    client.post("/api/v1/auth/register", json=user_data)

    # Get token
    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": user_data["username"],
            "password": user_data["password"]
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    return response.json()["access_token"]

@pytest.fixture
def auth_headers(auth_token):
    """Return authorization headers with the token."""
    return {"Authorization": f"Bearer {auth_token}"}

def test_register_user(client, user_data):
    """Test user registration."""
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201

    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "id" in data
    assert "password" not in data  # Password should not be returned

def test_login(client, registered_user, user_data):
    """Test user login and token generation."""
    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": user_data["username"],
            "password": user_data["password"]
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_get_current_user(client, auth_headers, registered_user):
    """Test getting the current user profile."""
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["username"] == registered_user["username"]
    assert data["email"] == registered_user["email"]

def test_login_invalid_credentials(client, registered_user):
    """Test login with invalid credentials."""
    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": registered_user["username"],
            "password": "wrongpassword"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 401

def test_auth_success(client, auth_headers):
    response = client.get("/test", headers=auth_headers)
    assert response.status_code == 200
    assert "message" in response.json()


def test_auth_missing_token(client):
    response = client.get("/test")
    assert response.status_code == 401
    assert "detail" in response.json()


def test_auth_empty_token(client):
    response = client.get("/test", headers={"Authorization": "Bearer "})
    assert response.status_code == 401
    assert "detail" in response.json()


def test_auth_wrong_scheme(client):
    response = client.get("/test", headers={"Authorization": "Basic test-token"})
    assert response.status_code == 401
    assert "detail" in response.json()