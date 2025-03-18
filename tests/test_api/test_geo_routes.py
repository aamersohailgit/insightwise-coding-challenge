# tests/test_api/test_geo_routes.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import json

from app.features.geo.service import GeoService
from app.main import app
from app.utils.errors import ExternalServiceError

@pytest.fixture
def client():
    """Test client for the API"""
    return TestClient(app)

@pytest.fixture
def mock_auth_headers():
    """Mock authentication headers"""
    return {"Authorization": "Bearer test_token"}

@pytest.fixture
def mock_geo_service():
    """Mock GeoService to avoid external API calls"""
    with patch("app.features.geo.routes.geo_service") as mock:
        yield mock

def test_get_location_by_postcode_success(client, mock_auth_headers, mock_geo_service):
    """Test successful location data retrieval"""
    # Setup mock service response
    mock_geo_service.get_location_data = AsyncMock(
        return_value={
            "latitude": 40.7506,
            "longitude": -73.9971
        }
    )

    # Make request
    response = client.post(
        "/api/v1/geo/location",
        json={"postcode": "10001"},
        headers=mock_auth_headers
    )

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["latitude"] == 40.7506
    assert data["longitude"] == -73.9971

    # Verify service call
    mock_geo_service.get_location_data.assert_called_once_with("10001")

def test_get_location_by_postcode_error(client, mock_auth_headers, mock_geo_service):
    """Test error handling for location data retrieval"""
    # Setup mock service to raise exception
    mock_geo_service.get_location_data = AsyncMock(
        side_effect=ExternalServiceError(
            message="Error fetching location data",
            details={"postcode": "invalid"}
        )
    )

    # Make request
    response = client.post(
        "/api/v1/geo/location",
        json={"postcode": "invalid"},
        headers=mock_auth_headers
    )

    # Verify response
    assert response.status_code == 502
    data = response.json()
    assert "Could not fetch location data" in data["detail"]

    # Verify service call
    mock_geo_service.get_location_data.assert_called_once_with("invalid")

def test_get_location_by_postcode_missing_postcode(client, mock_auth_headers):
    """Test error handling for missing postcode"""
    # Make request without postcode
    response = client.post(
        "/api/v1/geo/location",
        json={},
        headers=mock_auth_headers
    )

    # Verify response
    assert response.status_code == 422
    data = response.json()
    # The response format is different from standard FastAPI validation errors
    # It has a custom error structure
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert "details" in data["error"]
    assert "errors" in data["error"]["details"]

    # Check that there's an error for missing postcode field
    errors = data["error"]["details"]["errors"]
    assert len(errors) > 0

    # Check for validation error with postcode
    postcode_error = next((error for error in errors if "postcode" in error["location"]), None)
    assert postcode_error is not None
    assert postcode_error["type"] == "missing"

def test_get_location_by_postcode_server_error(client, mock_auth_headers, mock_geo_service):
    """Test error handling for unexpected errors"""
    # Setup mock service to raise unexpected exception
    mock_geo_service.get_location_data = AsyncMock(
        side_effect=Exception("Unexpected error")
    )

    # Make request
    response = client.post(
        "/api/v1/geo/location",
        json={"postcode": "10001"},
        headers=mock_auth_headers
    )

    # Verify response
    assert response.status_code == 500
    data = response.json()
    assert "An error occurred" in data["detail"]

    # Verify service call
    mock_geo_service.get_location_data.assert_called_once_with("10001")