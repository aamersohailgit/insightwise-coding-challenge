from fastapi import APIRouter, HTTPException, status

from app.features.geo.schemas import GeoData, PostcodeRequest
from app.features.geo.service import geo_service
from app.utils.errors import ExternalServiceError

router = APIRouter(prefix="/geo", tags=["geo"])

@router.post("/location", response_model=GeoData)
async def get_location_by_postcode(request: PostcodeRequest):
    try:
        location_data = await geo_service.get_location_data(request.postcode)
        return GeoData(**location_data)
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Could not fetch location data: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the request: {str(e)}"
        )
