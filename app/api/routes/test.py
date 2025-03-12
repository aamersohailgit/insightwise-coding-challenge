import logging
from fastapi import APIRouter, Depends, status

from app.api.middlewares.auth import require_auth

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/test", tags=["test"])

@router.get(
    "",
    status_code=status.HTTP_200_OK,
)
async def test_auth(token: str = Depends(require_auth)):
    """Test authentication middleware."""
    logger.info("Test authentication endpoint called")
    return {"message": "Authentication successful", "token": token}