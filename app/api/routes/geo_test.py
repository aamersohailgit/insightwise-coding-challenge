import logging
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.middlewares.auth import require_auth
from app.services.geo_service import GeoService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/geo-test", tags=["test"])

@router.get(
    "/{postcode}",
    status_code=status.HTTP_200_OK,
)
async def test_geo_service(postcode: str, token: str = Depends(require_auth)):
    """Test geo service with a postal code."""
    logger.info(f"Testing geo service with postcode: {postcode}")

    result = await GeoService.get_coordinates(postcode)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No location data found for postcode: {postcode}"
        )

    return result