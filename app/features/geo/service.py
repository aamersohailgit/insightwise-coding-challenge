import httpx
import logging
from typing import Dict, Any, Optional, Tuple

from app.features.geo.models import GeoCache
from app.utils.errors import ExternalServiceError
from app.config import config

logger = logging.getLogger(__name__)

class GeoService:
    @staticmethod
    async def get_location_data(postcode: str) -> Dict[str, float]:
        """Get location data for a US postcode."""
        # Check cache first
        cached = GeoCache.objects(postcode=postcode).first()
        if cached:
            logger.info(f"Using cached geo data for postcode {postcode}")
            return {
                "latitude": cached.latitude,
                "longitude": cached.longitude
            }

        # Fetch from API if not cached
        try:
            latitude, longitude = await GeoService._fetch_from_api(postcode)

            # Cache the result
            geo_cache = GeoCache(
                postcode=postcode,
                latitude=latitude,
                longitude=longitude
            )
            geo_cache.save()

            return {
                "latitude": latitude,
                "longitude": longitude
            }
        except Exception as e:
            logger.error(f"Error fetching location data for {postcode}: {str(e)}")
            raise

    @staticmethod
    async def _fetch_from_api(postcode: str) -> Tuple[float, float]:
        """Fetch location data from external API."""
        try:
            async with httpx.AsyncClient() as client:
                url = config.ZIPOPOTAM_API_URL.format(postcode=postcode)
                logger.info(f"Fetching geo data from {url}")

                response = await client.get(url, timeout=10.0)

                if response.status_code != 200:
                    raise ExternalServiceError(
                        message=f"Error fetching location data: {response.status_code}",
                        details={"postcode": postcode, "status": response.status_code}
                    )

                data = response.json()

                # Extract latitude and longitude
                places = data.get("places", [])
                if not places:
                    raise ExternalServiceError(
                        message="No location data found for postcode",
                        details={"postcode": postcode}
                    )

                latitude = float(places[0].get("latitude", 0))
                longitude = float(places[0].get("longitude", 0))

                return latitude, longitude
        except httpx.RequestError as e:
            logger.error(f"HTTP request failed: {str(e)}")
            raise ExternalServiceError(
                message=f"Error connecting to location service: {str(e)}",
                details={"postcode": postcode}
            )

    @staticmethod
    def calculate_direction(latitude: float, longitude: float) -> str:
        """Calculate direction from New York based on coordinates."""
        ny_lat = config.NEW_YORK_LAT
        ny_lon = config.NEW_YORK_LON

        is_north = latitude >= ny_lat
        is_east = longitude >= ny_lon

        if is_north and is_east:
            return "NE"
        elif is_north and not is_east:
            return "NW"
        elif not is_north and is_east:
            return "SE"
        else:
            return "SW"

geo_service = GeoService()
