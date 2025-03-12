import logging
import time
from typing import Dict, List, Optional, Any

import mongoengine
from app.models.item import Item
from app.core.events import event_emitter
from app.core.logging_config import get_logger, log_database_operation, log_operation_start, log_operation_success, log_operation_failed

logger = get_logger(__name__)

class ItemRepository:
    """Repository for Item model operations."""

    @classmethod
    async def create_item(cls, item_data: Dict[str, Any]) -> Item:
        """Create a new Item."""
        operation = f"create_item for {item_data.get('name')}"
        log_operation_start(logger, operation, item_name=item_data.get('name'))
        start_time = time.time()

        try:
            log_database_operation(
                logger,
                "insert",
                "items",
                {"name": item_data.get('name')},
                **{"data_fields": list(item_data.keys())}
            )

            item = Item(**item_data)
            item.save()

            duration_ms = round((time.time() - start_time) * 1000, 2)
            log_operation_success(
                logger,
                operation,
                duration_ms,
                item_id=str(item.id),
                item_name=item.name
            )

            event_emitter.emit("item.created", str(item.id), item.to_dict())

            return item
        except Exception as e:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            log_operation_failed(
                logger,
                operation,
                e,
                duration_ms,
                item_data=item_data
            )
            raise

    @classmethod
    async def get_item_by_id(cls, item_id: str) -> Optional[Item]:
        """Get Item by ID."""
        operation = f"get_item_by_id: {item_id}"
        log_operation_start(logger, operation, item_id=item_id)
        start_time = time.time()

        try:
            log_database_operation(
                logger,
                "find_one",
                "items",
                {"id": item_id}
            )

            item = Item.objects.get(id=item_id)

            duration_ms = round((time.time() - start_time) * 1000, 2)
            log_operation_success(
                logger,
                operation,
                duration_ms,
                item_id=str(item.id),
                item_name=item.name
            )

            return item
        except (Item.DoesNotExist, mongoengine.errors.ValidationError) as e:
            # This handles both "not found" and "invalid ID format" cases
            duration_ms = round((time.time() - start_time) * 1000, 2)
            logger.warning(
                f"Item not found or invalid ID: {item_id}",
                extra={
                    "item_id": item_id,
                    "error": str(e),
                    "duration_ms": duration_ms
                }
            )
            return None
        except Exception as e:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            log_operation_failed(
                logger,
                operation,
                e,
                duration_ms,
                item_id=item_id
            )
            raise

    @classmethod
    async def get_all_items(cls) -> List[Item]:
        """Get all Items."""
        operation = "get_all_items"
        log_operation_start(logger, operation)
        start_time = time.time()

        try:
            log_database_operation(
                logger,
                "find_all",
                "items"
            )

            items = list(Item.objects.all())

            duration_ms = round((time.time() - start_time) * 1000, 2)
            log_operation_success(
                logger,
                operation,
                duration_ms,
                items_count=len(items)
            )

            return items
        except Exception as e:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            log_operation_failed(
                logger,
                operation,
                e,
                duration_ms
            )
            raise

    @classmethod
    async def update_item(cls, item_id: str, update_data: Dict[str, Any]) -> Optional[Item]:
        """Update Item."""
        operation = f"update_item: {item_id}"
        log_operation_start(
            logger,
            operation,
            item_id=item_id,
            fields_to_update=list(update_data.keys())
        )
        start_time = time.time()

        try:
            item = await cls.get_item_by_id(item_id)
            if not item:
                duration_ms = round((time.time() - start_time) * 1000, 2)
                logger.warning(
                    f"Item not found for update: {item_id}",
                    extra={
                        "item_id": item_id,
                        "fields_to_update": list(update_data.keys()),
                        "duration_ms": duration_ms
                    }
                )
                return None

            # Update only allowed fields
            for field, value in update_data.items():
                if field in ['name', 'title', 'users', 'start_date', 'postcode']:
                    setattr(item, field, value)

            log_database_operation(
                logger,
                "update",
                "items",
                {"id": item_id},
                **{"fields_updated": list(update_data.keys())}
            )

            item.save()

            duration_ms = round((time.time() - start_time) * 1000, 2)
            log_operation_success(
                logger,
                operation,
                duration_ms,
                item_id=str(item.id),
                item_name=item.name,
                fields_updated=list(update_data.keys())
            )

            event_emitter.emit("item.updated", item_id, update_data)

            return item
        except Exception as e:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            log_operation_failed(
                logger,
                operation,
                e,
                duration_ms,
                item_id=item_id,
                update_data=update_data
            )
            raise

    @classmethod
    async def delete_item(cls, item_id: str) -> bool:
        """Delete Item."""
        operation = f"delete_item: {item_id}"
        log_operation_start(logger, operation, item_id=item_id)
        start_time = time.time()

        try:
            item = await cls.get_item_by_id(item_id)
            if not item:
                duration_ms = round((time.time() - start_time) * 1000, 2)
                logger.warning(
                    f"Item not found for deletion: {item_id}",
                    extra={
                        "item_id": item_id,
                        "duration_ms": duration_ms
                    }
                )
                return False

            log_database_operation(
                logger,
                "delete",
                "items",
                {"id": item_id}
            )

            item.delete()

            duration_ms = round((time.time() - start_time) * 1000, 2)
            log_operation_success(
                logger,
                operation,
                duration_ms,
                item_id=item_id,
                item_name=item.name
            )

            event_emitter.emit("item.deleted", item_id)

            return True
        except Exception as e:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            log_operation_failed(
                logger,
                operation,
                e,
                duration_ms,
                item_id=item_id
            )
            raise

    @classmethod
    async def update_geo_data(cls, item_id: str, geo_data: Dict[str, Any]) -> Optional[Item]:
        """Update geolocation data for an Item."""
        operation = f"update_geo_data: {item_id}"
        log_operation_start(
            logger,
            operation,
            item_id=item_id,
            geo_data=geo_data
        )
        start_time = time.time()

        try:
            item = await cls.get_item_by_id(item_id)
            if not item:
                duration_ms = round((time.time() - start_time) * 1000, 2)
                logger.warning(
                    f"Item not found for geo update: {item_id}",
                    extra={
                        "item_id": item_id,
                        "geo_data": geo_data,
                        "duration_ms": duration_ms
                    }
                )
                return None

            item.latitude = geo_data.get("latitude")
            item.longitude = geo_data.get("longitude")
            item.direction_from_new_york = geo_data.get("direction_from_new_york")

            log_database_operation(
                logger,
                "update_geo",
                "items",
                {"id": item_id},
                **{
                    "latitude": geo_data.get("latitude"),
                    "longitude": geo_data.get("longitude"),
                    "direction": geo_data.get("direction_from_new_york")
                }
            )

            item.save()

            duration_ms = round((time.time() - start_time) * 1000, 2)
            log_operation_success(
                logger,
                operation,
                duration_ms,
                item_id=str(item.id),
                item_name=item.name,
                geo_data=geo_data
            )

            return item
        except Exception as e:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            log_operation_failed(
                logger,
                operation,
                e,
                duration_ms,
                item_id=item_id,
                geo_data=geo_data
            )
            raise