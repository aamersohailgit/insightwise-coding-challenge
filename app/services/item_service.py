import logging
from typing import Dict, List, Optional, Any

from app.models.item import Item
from app.repositories.item_repository import ItemRepository
from app.services.geo_service import GeoService
from app.utils.case_converter import camel_to_snake_dict, snake_to_camel_dict
from app.core.logging_config import get_logger
from app.utils.api_error_handler import ApiError

logger = get_logger(__name__)

class ItemService:
    """Service for handling Item-related business logic."""

    @classmethod
    async def create_item(cls, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Item."""
        logger.info(f"Service: Creating new item with name: {item_data.get('name')}",
                    extra={"item_name": item_data.get('name')})

        snake_case_data = camel_to_snake_dict(item_data)

        if 'name' in snake_case_data and 'users' in snake_case_data:
            if snake_case_data['name'] not in snake_case_data['users']:
                logger.warning("Name not in users list, adding it automatically",
                              extra={"name": snake_case_data['name']})
                snake_case_data['users'].append(snake_case_data['name'])

        item = await ItemRepository.create_item(snake_case_data)

        # Try to fetch geo data, but don't fail if it's not available
        try:
            geo_data = await GeoService.get_coordinates(item.postcode)
            if geo_data:
                item = await ItemRepository.update_geo_data(str(item.id), geo_data)
            else:
                logger.warning(f"No geo data returned for postcode: {item.postcode}",
                              extra={"item_id": str(item.id), "postcode": item.postcode})
        except ApiError as e:
            logger.error(
                f"Failed to get geo data for item {str(item.id)}, but item was created successfully",
                extra={
                    "item_id": str(item.id),
                    "postcode": item.postcode,
                    "error": str(e),
                    "error_details": e.details if hasattr(e, 'details') else {}
                }
            )
            # Item is created successfully but without geo data
            # We could retry or queue for later processing
        except Exception as e:
            logger.exception(
                f"Unexpected error getting geo data for item {str(item.id)}",
                extra={"item_id": str(item.id), "postcode": item.postcode}
            )
            # Item is created successfully but without geo data

        return snake_to_camel_dict(item.to_dict())

    @classmethod
    async def get_item(cls, item_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific Item."""
        logger.debug(f"Service: Fetching item: {item_id}",
                    extra={"item_id": item_id})

        item = await ItemRepository.get_item_by_id(item_id)
        if not item:
            logger.warning(f"Item not found: {item_id}",
                          extra={"item_id": item_id})
            return None

        return snake_to_camel_dict(item.to_dict())

    @classmethod
    async def get_all_items(cls) -> List[Dict[str, Any]]:
        """Get all Items."""
        logger.debug("Service: Fetching all items")

        items = await ItemRepository.get_all_items()
        logger.info(f"Fetched {len(items)} items")

        return [snake_to_camel_dict(item.to_dict()) for item in items]

    @classmethod
    async def update_item(cls, item_id: str, item_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an Item."""
        logger.info(f"Service: Updating item: {item_id}",
                   extra={"item_id": item_id, "update_fields": list(item_data.keys())})

        snake_case_data = camel_to_snake_dict(item_data)

        item = await ItemRepository.update_item(item_id, snake_case_data)
        if not item:
            logger.warning(f"Item not found for update: {item_id}",
                          extra={"item_id": item_id})
            return None

        # If postcode was updated, refresh geo data
        if 'postcode' in snake_case_data:
            try:
                logger.info(f"Postcode updated, refreshing geo data for item: {item_id}",
                           extra={"item_id": item_id, "new_postcode": item.postcode})
                geo_data = await GeoService.get_coordinates(item.postcode)
                if geo_data:
                    item = await ItemRepository.update_geo_data(item_id, geo_data)
                else:
                    logger.warning(f"No geo data returned for updated postcode: {item.postcode}",
                                  extra={"item_id": item_id, "postcode": item.postcode})
            except ApiError as e:
                logger.error(
                    f"Failed to update geo data for item {item_id}, but item was updated successfully",
                    extra={
                        "item_id": item_id,
                        "postcode": item.postcode,
                        "error": str(e),
                        "error_details": e.details if hasattr(e, 'details') else {}
                    }
                )
            except Exception as e:
                logger.exception(
                    f"Unexpected error updating geo data for item {item_id}",
                    extra={"item_id": item_id, "postcode": item.postcode}
                )

        return snake_to_camel_dict(item.to_dict())

    @classmethod
    async def delete_item(cls, item_id: str) -> bool:
        """Delete an Item."""
        logger.info(f"Service: Deleting item: {item_id}",
                   extra={"item_id": item_id})

        result = await ItemRepository.delete_item(item_id)
        if not result:
            logger.warning(f"Item not found for deletion: {item_id}",
                          extra={"item_id": item_id})

        return result