from typing import List
from fastapi import APIRouter, Path, HTTPException, status, Depends

from app.features.items.schemas import ItemCreate, ItemUpdate, ItemResponse
from app.features.items.service import ItemService, ItemServiceInterface, item_service
from app.utils.errors import NotFoundError, ValidationError, ExternalServiceError

router = APIRouter(prefix="/items", tags=["items"])

def get_item_service() -> ItemServiceInterface:
    """Dependency to get the item service"""
    return item_service

@router.get("/", response_model=List[ItemResponse])
async def get_all_items(
    item_service: ItemServiceInterface = Depends(get_item_service)
):
    items = await item_service.get_all_items()
    return [ItemResponse(**item.to_dict()) for item in items]

@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: str = Path(..., description="The ID of the item to retrieve"),
    item_service: ItemServiceInterface = Depends(get_item_service)
):
    try:
        item = await item_service.get_item_by_id(item_id)
        return ItemResponse(**item.to_dict())
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)

@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    item_data: ItemCreate,
    item_service: ItemServiceInterface = Depends(get_item_service)
):
    try:
        item = await item_service.create_item(item_data)
        return ItemResponse(**item.to_dict())
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message)
    except ExternalServiceError as e:
        # Create the item without geo data but inform the client
        raise HTTPException(
            status_code=status.HTTP_207_MULTI_STATUS,
            detail=f"Item created but geo data could not be fetched: {e.message}"
        )

@router.patch("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_data: ItemUpdate,
    item_id: str = Path(..., description="The ID of the item to update"),
    item_service: ItemServiceInterface = Depends(get_item_service)
):
    try:
        item = await item_service.update_item(item_id, item_data)
        return ItemResponse(**item.to_dict())
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message)

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: str = Path(..., description="The ID of the item to delete"),
    item_service: ItemServiceInterface = Depends(get_item_service)
):
    try:
        await item_service.delete_item(item_id)
        return None
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
