import logging
from typing import Dict, Optional

import httpx

from app.core.events import event_emitter
from app.core.logging_config import get_logger
from app.utils.api_error_handler import handle_api_errors, log_request_response
from app.utils.retry import async_retry

logger = get_logger(__name__)

# Constants for New York coordinates (zipcode 10001)
NY_LATITUDE = 40.7506
NY_LONGITUDE = -73.9971

class GeoService:
    """Service for handling geolocation operations."""

    API_BASE_URL = "https://api.zippopotam.us/us/"

    @classmethod
    @handle_api_errors("geo_lookup")
    @async_retry(
        retries=3,
        delay=1.0,
        backoff_factor=2.0,
        exceptions=[httpx.TransportError, httpx.TimeoutException]
    )
    async def get_coordinates(cls, postcode: str) -> Optional[Dict]:
        """Get coordinates for a postal code using the zippopotam.us API."""
        logger.info(f"Fetching coordinates for postcode: {postcode}",
                   extra={"postcode": postcode})

        async with httpx.AsyncClient(timeout=10.0) as client:
            request = client.build_request("GET", f"{cls.API_BASE_URL}{postcode}")
            response = await client.send(request)

            # Log the API request/response
            await log_request_response(request, response)

            # Raise for HTTP errors (will be caught by decorator)
            response.raise_for_status()

            data = response.json()

            # Extract coordinates
            places = data.get("places", [])
            if not places:
                logger.warning(
                    f"No location data found for postcode: {postcode}",
                    extra={"postcode": postcode, "response": data}
                )
                event_emitter.emit("geo.lookup.error", postcode, "No location data found")
                return None

            place = places[0]
            latitude = float(place.get("latitude"))
            longitude = float(place.get("longitude"))

            result = {
                "latitude": latitude,
                "longitude": longitude,
                "direction_from_new_york": cls.calculate_direction(latitude, longitude)
            }

            logger.info(
                f"Successfully fetched coordinates for postcode: {postcode}",
                extra={"postcode": postcode, "coordinates": {"lat": latitude, "lon": longitude}}
            )
            event_emitter.emit("geo.lookup.success", postcode, result)
            return result

    @staticmethod
    def calculate_direction(latitude: float, longitude: float) -> str:
        """Calculate direction from New York based on coordinates."""
        is_north = latitude >= NY_LATITUDE
        is_east = longitude >= NY_LONGITUDE

        if is_north and is_east:
            return "NE"
        elif is_north and not is_east:
            return "NW"
        elif not is_north and is_east:
            return "SE"
        else:
            return "SW"