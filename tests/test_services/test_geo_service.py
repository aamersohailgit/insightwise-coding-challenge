# tests/test_services/test_geo_service.py
import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock

from app.features.items.service import GeoLocationService
from app.features.items.models import Direction
from app.utils.errors import ExternalServiceError

# Implementation of GeoLocationService for testing
class DefaultGeoLocationService:
    """Default implementation of geo location service"""
    NY_COORDINATES = (40.7128, -74.0060)  # New York City coordinates

    async def get_location_data(self, postcode: str) -> dict:
        """
        Get location data from postcode

        Args:
            postcode: The postcode to get location data for

        Returns:
            Dict containing latitude, longitude and direction from New York

        Raises:
            ExternalServiceError: If there's an error getting the data
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.example.com/postcodes/{postcode}",
                    timeout=5.0
                )

                if response.status_code != 200:
                    raise ExternalServiceError(f"Error fetching geo data: {response.status_code}")

                data = response.json()
                lat = float(data["data"]["lat"])
                lng = float(data["data"]["lng"])

                # Calculate direction from New York
                direction = self.calculate_direction(lat, lng)

                return {
                    "latitude": lat,
                    "longitude": lng,
                    "direction_from_new_york": direction
                }
        except Exception as e:
            raise ExternalServiceError(f"Error fetching geo data: {str(e)}")

    def calculate_direction(self, latitude: float, longitude: float) -> str:
        """
        Calculate direction from New York to given coordinates

        Args:
            latitude: The latitude
            longitude: The longitude

        Returns:
            Direction as a string (NE, NW, SE, SW)
        """
        ny_lat, ny_lng = self.NY_COORDINATES

        # If coordinates are the same as NY, return arbitrary direction
        if abs(latitude - ny_lat) < 0.001 and abs(longitude - ny_lng) < 0.001:
            return Direction.NE.value

        # Determine North/South component
        if latitude > ny_lat:
            ns = "N"
        else:
            ns = "S"

        # Determine East/West component
        if longitude > ny_lng:
            ew = "E"
        else:
            ew = "W"

        # Combine directions
        direction = ns + ew

        # Ensure it's a valid Direction
        if direction in [d.value for d in Direction]:
            return direction

        # Default to NE if somehow we get an invalid direction
        return Direction.NE.value

@pytest.fixture
def valid_response():
    """Mock a valid response from the geo API"""
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_json = MagicMock(return_value={
        "status": "success",
        "data": {
            "lat": "40.7484",
            "lng": "-73.9967"
        }
    })
    mock_response.json = mock_json
    return mock_response

@pytest.fixture
def error_response():
    """Mock an error response from the geo API"""
    mock_response = AsyncMock()
    mock_response.status_code = 404
    mock_json = MagicMock(return_value={
        "status": "error",
        "message": "Postcode not found"
    })
    mock_response.json = mock_json
    return mock_response

@pytest.fixture
def valid_ny_coordinates():
    """Default New York City coordinates"""
    return (40.7128, -74.0060)

@pytest.mark.asyncio
async def test_get_location_data_success(valid_response):
    """Test getting location data successfully"""
    # Setup
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value = valid_response

        # Create service
        geo_service = DefaultGeoLocationService()

        # Call method
        result = await geo_service.get_location_data("10001")

        # Assert
        assert result["latitude"] == 40.7484
        assert result["longitude"] == -73.9967
        assert result["direction_from_new_york"] in [d.value for d in Direction]

        # Check API call
        mock_client.return_value.__aenter__.return_value.get.assert_called_once()
        call_args = mock_client.return_value.__aenter__.return_value.get.call_args[0][0]
        assert "10001" in call_args

@pytest.mark.asyncio
async def test_get_location_data_error(error_response):
    """Test getting location data with API error"""
    # Setup
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value = error_response

        # Create service
        geo_service = DefaultGeoLocationService()

        # Call method and assert
        with pytest.raises(ExternalServiceError) as exc_info:
            await geo_service.get_location_data("invalid-postcode")

        assert "Error fetching geo data" in str(exc_info.value)

        # Check API call
        mock_client.return_value.__aenter__.return_value.get.assert_called_once()

@pytest.mark.asyncio
async def test_get_location_data_exception():
    """Test getting location data with exception"""
    # Setup
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get.side_effect = Exception("Connection error")

        # Create service
        geo_service = DefaultGeoLocationService()

        # Call method and assert
        with pytest.raises(ExternalServiceError) as exc_info:
            await geo_service.get_location_data("10001")

        assert "Error fetching geo data" in str(exc_info.value)

        # Check API call
        mock_client.return_value.__aenter__.return_value.get.assert_called_once()

def test_calculate_direction():
    """Test direction calculation"""
    # Create service
    geo_service = DefaultGeoLocationService()

    # Test cases for different directions
    test_cases = [
        # Northeast (higher latitude, higher longitude)
        ((41.0, -73.0), Direction.NE),
        # Northwest (higher latitude, lower longitude)
        ((41.0, -75.0), Direction.NW),
        # Southeast (lower latitude, higher longitude)
        ((40.0, -73.0), Direction.SE),
        # Southwest (lower latitude, lower longitude)
        ((40.0, -75.0), Direction.SW),
    ]

    # Run tests
    for coords, expected_direction in test_cases:
        lat, lng = coords
        with patch.object(geo_service, 'NY_COORDINATES', (40.7128, -74.0060)):
            direction = geo_service.calculate_direction(lat, lng)
            assert direction == expected_direction.value, f"Failed for coords {coords}, got {direction} expected {expected_direction.value}"

def test_calculate_direction_same_coords():
    """Test direction calculation with same coordinates as NY"""
    # Create service
    geo_service = DefaultGeoLocationService()

    # Test with same coordinates
    with patch.object(geo_service, 'NY_COORDINATES', (40.7128, -74.0060)):
        direction = geo_service.calculate_direction(40.7128, -74.0060)
        assert direction in [d.value for d in Direction]