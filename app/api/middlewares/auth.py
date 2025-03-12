import logging
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger(__name__)

class BearerAuth(HTTPBearer):
    """Bearer token authentication handler."""

    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=False)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials:
        """Validate Bearer token from request."""
        credentials = await super().__call__(request)

        # Check if credentials are missing or invalid
        if not credentials:
            logger.warning("Missing authentication")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authentication",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check authentication scheme
        if credentials.scheme.lower() != "bearer":
            logger.warning("Invalid authentication scheme")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check token (any non-empty string is acceptable per requirements)
        if not credentials.credentials or credentials.credentials.strip() == "":
            logger.warning("Invalid token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return credentials

bearer_auth = BearerAuth()

def require_auth(auth: HTTPAuthorizationCredentials = Depends(bearer_auth)) -> str:
    """Authentication dependency for routes."""
    return auth.credentials