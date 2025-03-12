import logging
from typing import Dict, List, Optional, Any

from app.models.item import Item
from app.core.events import event_emitter

logger = logging.getLogger(__name__)

class ItemRepository:
    """Repository for Item model operations."""

    @classmethod
    async def create_item(cls, item_data: Dict[str, Any]) -> Item:
        """Create a new Item."""
        logger.info(f"Creating new item with name: {item_data.get('name')}")

        try:
            item = Item(**item_data)
            item.save()

            event_emitter.emit("item.created", str(item.id), item.to_dict())

            return item
        except Exception as e:
            logger.exception(f"Error creating item: {str(e)}")
            raise

    @classmethod
    async def get_item_by_id(cls, item_id: str) -> Optional[Item]:
        """Get Item by ID."""
        logger.debug(f"Fetching item with ID: {item_id}")

        try:
            return Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            logger.warning(f"Item not found: {item_id}")
            return None
        except Exception as e:
            logger.exception(f"Error fetching item {item_id}: {str(e)}")
            raise

    @classmethod
    async def get_all_items(cls) -> List[Item]:
        """Get all Items."""
        logger.debug("Fetching all items")

        try:
            return list(Item.objects.all())
        except Exception as e:
            logger.exception(f"Error fetching all items: {str(e)}")
            raise

    @classmethod
    async def update_item(cls, item_id: str, update_data: Dict[str, Any]) -> Optional[Item]:
        """Update Item."""
        logger.info(f"Updating item {item_id}")

        try:
            item = await cls.get_item_by_id(item_id)
            if not item:
                return None

            # Update only allowed fields
            for field, value in update_data.items():
                if field in ['name', 'title', 'users', 'start_date']:
                    setattr(item, field, value)

            item.save()

            event_emitter.emit("item.updated", item_id, update_data)

            return item
        except Exception as e:
            logger.exception(f"Error updating item {item_id}: {str(e)}")
            raise

    @classmethod
    async def delete_item(cls, item_id: str) -> bool:
        """Delete Item."""
        logger.info(f"Deleting item {item_id}")

        try:
            item = await cls.get_item_by_id(item_id)
            if not item:
                return False

            item.delete()

            event_emitter.emit("item.deleted", item_id)

            return True
        except Exception as e:
            logger.exception(f"Error deleting item {item_id}: {str(e)}")
            raise

    @classmethod
    async def update_geo_data(cls, item_id: str, geo_data: Dict[str, Any]) -> Optional[Item]:
        """Update geolocation data for an Item."""
        logger.info(f"Updating geolocation data for item {item_id}")

        try:
            item = await cls.get_item_by_id(item_id)
            if not item:
                return None

            item.latitude = geo_data.get("latitude")
            item.longitude = geo_data.get("longitude")
            item.direction_from_new_york = geo_data.get("direction_from_new_york")

            item.save()

            return item
        except Exception as e:
            logger.exception(f"Error updating geo data for item {item_id}: {str(e)}")
            raise