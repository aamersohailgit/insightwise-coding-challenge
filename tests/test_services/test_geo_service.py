# tests/test_services/test_geo_service.py
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import json
import httpx

from app.services.geo_service import GeoService
from app.utils.api_error_handler import ApiError


class MockResponse:
    def __init__(self, json_data, status_code=200):
        self.json_data = json_data
        self.status_code = status_code
        self.text = json.dumps(json_data)
        self.headers = {}
        self.url = "https://api.zippopotam.us/us/test"
        self.request = MagicMock()
        self.request.method = "GET"
        self.request.url = self.url
        self.request.headers = {}
        self._request = self.request
        self.has_redirect_location = False
        self.is_success = status_code < 400
        self.reason_phrase = "OK" if status_code < 400 else "Not Found"

    def json(self):
        return self.json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                f"HTTP Error: {self.status_code}",
                request=self.request,
                response=self
            )


class MockAsyncClient:
    def __init__(self, mock_response, *args, **kwargs):
        self.mock_response = mock_response
        self.send = AsyncMock(return_value=mock_response)
        self.build_request = MagicMock(return_value=MagicMock())

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.mark.asyncio
async def test_get_coordinates_success():
    # Set up the test response data
    test_data = {
        "post code": "10001",
        "country": "United States",
        "places": [
            {
                "latitude": "40.7128",
                "longitude": "-74.0060"
            }
        ]
    }

    # Create a mock response with our test data
    mock_response = MockResponse(test_data)

    # Create a context manager factory that returns our mock client
    def mock_async_client(*args, **kwargs):
        return MockAsyncClient(mock_response)

    # Test with patching
    with patch('httpx.AsyncClient', mock_async_client), \
         patch('app.core.events.event_emitter.emit'):

        # Call the method
        result = await GeoService.get_coordinates("10001")

        # Check the result
        assert result is not None
        assert result["latitude"] == float(test_data["places"][0]["latitude"])
        assert result["longitude"] == float(test_data["places"][0]["longitude"])
        assert result["direction_from_new_york"] in ["NE", "NW", "SE", "SW"]


@pytest.mark.asyncio
async def test_get_coordinates_error():
    # Create a mock response with a 404 status code
    mock_response = MockResponse({}, 404)

    # Create a context manager factory that returns our mock client
    def mock_async_client(*args, **kwargs):
        return MockAsyncClient(mock_response)

    # Test with patching
    with patch('httpx.AsyncClient', mock_async_client), \
         patch('app.core.events.event_emitter.emit'):

        # Call the method - we expect it to raise ApiError
        with pytest.raises(ApiError) as excinfo:
            await GeoService.get_coordinates("invalid")

        # Verify the error contains the expected status code
        assert excinfo.value.status_code == 404
        assert "External API error: 404" in str(excinfo.value)


def test_calculate_direction():
    # Test NorthEast
    assert GeoService.calculate_direction(41.0, -73.0) == "NE"

    # Test NorthWest
    assert GeoService.calculate_direction(41.0, -74.5) == "NW"

    # Test SouthEast
    assert GeoService.calculate_direction(40.0, -73.0) == "SE"

    # Test SouthWest
    assert GeoService.calculate_direction(40.0, -74.5) == "SW"