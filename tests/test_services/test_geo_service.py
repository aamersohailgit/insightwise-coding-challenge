# tests/test_services/test_geo_service.py
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import json

from app.services.geo_service import GeoService


class MockResponse:
    def __init__(self, json_data, status_code=200):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data

    async def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP Error: {self.status_code}")


@pytest.mark.asyncio
async def test_get_coordinates_success():
    # Set up the test response data
    test_data = {
        "places": [
            {
                "latitude": "40.7128",
                "longitude": "-74.0060"
            }
        ]
    }

    mock_response = MockResponse(test_data)

    # Mock the client.get method
    async def mock_get(*args, **kwargs):
        return mock_response

    # Apply the mock
    with patch('httpx.AsyncClient.get', side_effect=mock_get):
        # Call the method
        result = await GeoService.get_coordinates("10001")

        # Check the result
        assert result is not None
        assert result["latitude"] == float(test_data["places"][0]["latitude"])
        assert result["longitude"] == float(test_data["places"][0]["longitude"])
        assert result["direction_from_new_york"] in ["NE", "NW", "SE", "SW"]


@pytest.mark.asyncio
async def test_get_coordinates_error():
    # Mock a failed response
    async def mock_get(*args, **kwargs):
        raise Exception("Connection error")

    # Apply the mock
    with patch('httpx.AsyncClient.get', side_effect=mock_get):
        # Call the method
        result = await GeoService.get_coordinates("invalid")

        # Check that we get None on error
        assert result is None


def test_calculate_direction():
    # Test NorthEast
    assert GeoService.calculate_direction(41.0, -73.0) == "NE"

    # Test NorthWest
    assert GeoService.calculate_direction(41.0, -74.5) == "NW"

    # Test SouthEast
    assert GeoService.calculate_direction(40.0, -73.0) == "SE"

    # Test SouthWest
    assert GeoService.calculate_direction(40.0, -74.5) == "SW"