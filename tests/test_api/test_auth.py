import pytest
from fastapi.testclient import TestClient


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