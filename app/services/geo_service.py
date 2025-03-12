import logging
from typing import Dict, Optional

import httpx

from app.core.events import event_emitter

logger = logging.getLogger(__name__)

# Constants for New York coordinates (zipcode 10001)
NY_LATITUDE = 40.7506
NY_LONGITUDE = -73.9971

class GeoService:
    """Service for handling geolocation operations."""

    API_BASE_URL = "https://api.zippopotam.us/us/"

    @classmethod
    async def get_coordinates(cls, postcode: str) -> Optional[Dict]:
        """Get coordinates for a postal code using the zippopotam.us API."""
        logger.info(f"Fetching coordinates for postcode: {postcode}")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{cls.API_BASE_URL}{postcode}")
                response.raise_for_status()

                data = response.json()

                # Extract coordinates
                places = data.get("places", [])
                if not places:
                    logger.warning(f"No location data found for postcode: {postcode}")
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

                event_emitter.emit("geo.lookup.success", postcode, result)
                return result

        except Exception as e:
            logger.exception(f"Error fetching coordinates for postcode {postcode}")
            event_emitter.emit("geo.lookup.error", postcode, str(e))
            return None

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