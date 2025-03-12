import logging
from typing import Dict, List, Optional, Any

from app.models.item import Item
from app.repositories.item_repository import ItemRepository
from app.services.geo_service import GeoService
from app.utils.case_converter import camel_to_snake_dict, snake_to_camel_dict

logger = logging.getLogger(__name__)

class ItemService:
    """Service for handling Item-related business logic."""

    @classmethod
    async def create_item(cls, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Item."""
        logger.info(f"Service: Creating new item with name: {item_data.get('name')}")

        snake_case_data = camel_to_snake_dict(item_data)

        if 'name' in snake_case_data and 'users' in snake_case_data:
            if snake_case_data['name'] not in snake_case_data['users']:
                logger.warning("Name not in users list, adding it automatically")
                snake_case_data['users'].append(snake_case_data['name'])

        item = await ItemRepository.create_item(snake_case_data)

        geo_data = await GeoService.get_coordinates(item.postcode)
        if geo_data:
            item = await ItemRepository.update_geo_data(str(item.id), geo_data)

        return snake_to_camel_dict(item.to_dict())

    @classmethod
    async def get_item(cls, item_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific Item."""
        logger.debug(f"Service: Fetching item: {item_id}")

        item = await ItemRepository.get_item_by_id(item_id)
        if not item:
            return None

        return snake_to_camel_dict(item.to_dict())

    @classmethod
    async def get_all_items(cls) -> List[Dict[str, Any]]:
        """Get all Items."""
        logger.debug("Service: Fetching all items")

        items = await ItemRepository.get_all_items()

        return [snake_to_camel_dict(item.to_dict()) for item in items]

    @classmethod
    async def update_item(cls, item_id: str, item_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an Item."""
        logger.info(f"Service: Updating item: {item_id}")

        snake_case_data = camel_to_snake_dict(item_data)

        item = await ItemRepository.update_item(item_id, snake_case_data)
        if not item:
            return None

        return snake_to_camel_dict(item.to_dict())

    @classmethod
    async def delete_item(cls, item_id: str) -> bool:
        """Delete an Item."""
        logger.info(f"Service: Deleting item: {item_id}")

        return await ItemRepository.delete_item(item_id)