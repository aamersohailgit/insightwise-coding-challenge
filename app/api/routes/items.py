import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, status
from fastapi.exceptions import RequestValidationError
from starlette.requests import Request

from app.api.middlewares.auth import require_auth
from app.schemas.item import ItemCreate, ItemUpdate, ItemResponse
from app.services.item_service import ItemService
from app.core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/items", tags=["items"])

@router.post(
    "",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_item(item: ItemCreate, token: str = Depends(require_auth)):
    """Create a new item."""
    logger.info(f"API: Create item request received for {item.name}")

    try:
        item_data = item.dict()

        if item.name not in item.users:
            error_msg = "Name must be included in Users list"
            logger.error(f"Validation error: {error_msg}",
                        extra={"item_name": item.name, "validation_error": error_msg})
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=error_msg
            )

        result = await ItemService.create_item(item_data)
        return result
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}",
                    extra={"validation_error": str(e), "item_data": item_data})
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.exception(f"Error creating item: {str(e)}",
                        extra={"error": str(e), "item_data": item_data})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get(
    "",
    response_model=List[ItemResponse],
)
async def get_all_items(token: str = Depends(require_auth)):
    """Get all items."""
    logger.info("API: Get all items request received")

    try:
        return await ItemService.get_all_items()
    except Exception as e:
        logger.exception(f"Error fetching items: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get(
    "/{item_id}",
    response_model=ItemResponse,
)
async def get_item(
    item_id: str = Path(..., title="The ID of the item to get"),
    token: str = Depends(require_auth)
):
    """Get a specific item by ID."""
    logger.info(f"API: Get item request received for ID {item_id}")

    try:
        item = await ItemService.get_item(item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
        return item
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error fetching item {item_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.patch(
    "/{item_id}",
    response_model=ItemResponse,
)
async def update_item(
    item: ItemUpdate,
    item_id: str = Path(..., title="The ID of the item to update"),
    token: str = Depends(require_auth)
):
    """Update an item."""
    logger.info(f"API: Update item request received for ID {item_id}")

    try:
        update_data = {k: v for k, v in item.dict().items() if v is not None}

        result = await ItemService.update_item(item_id, update_data)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
        return result
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error updating item {item_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_item(
    item_id: str = Path(..., title="The ID of the item to delete"),
    token: str = Depends(require_auth)
):
    """Delete an item."""
    logger.info(f"API: Delete item request received for ID {item_id}")

    try:
        result = await ItemService.delete_item(item_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error deleting item {item_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )