import logging
import httpx
import asyncio
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any, Protocol, runtime_checkable
from abc import ABC, abstractmethod

from app.features.items.models import Item, Direction
from app.features.items.schemas import ItemCreate, ItemUpdate
from app.features.items.validators import ItemValidator, item_validator
from app.utils.errors import NotFoundError, ValidationError, ExternalServiceError
from app.core.events import event_emitter
from app.config import config

logger = logging.getLogger(__name__)

@runtime_checkable
class GeoLocationService(Protocol):
    """Interface for geolocation services"""
    async def get_location_data(self, postcode: str) -> Dict[str, Any]: ...
    def calculate_direction(self, latitude: float, longitude: float) -> str: ...

@runtime_checkable
class EventEmitter(Protocol):
    """Interface for event emission"""
    def emit(self, event_name: str, data: Dict[str, Any] = None) -> None: ...

class ItemServiceInterface(ABC):
    """Interface for Item service operations"""

    @abstractmethod
    async def get_all_items(self) -> List[Item]:
        """Retrieve all items"""
        pass

    @abstractmethod
    async def get_item_by_id(self, item_id: str) -> Item:
        """Retrieve a specific item by ID"""
        pass

    @abstractmethod
    async def create_item(self, data: ItemCreate) -> Item:
        """Create a new item"""
        pass

    @abstractmethod
    async def update_item(self, item_id: str, data: ItemUpdate) -> Item:
        """Update an existing item"""
        pass

    @abstractmethod
    async def delete_item(self, item_id: str) -> bool:
        """Delete an item"""
        pass

class DefaultGeoLocationService:
    """Default implementation of geolocation service"""

    async def get_location_data(self, postcode: str) -> Dict[str, Any]:
        """Fetch location data for a postcode from the external API."""
        try:
            async with httpx.AsyncClient() as client:
                url = config.ZIPOPOTAM_API_URL.format(postcode=postcode)
                response = await client.get(url)

                if response.status_code != 200:
                    raise ExternalServiceError(
                        message=f"Error fetching location data: {response.status_code}",
                        details={"postcode": postcode, "status": response.status_code}
                    )

                data = response.json()

                latitude = float(data.get("places", [{}])[0].get("latitude", 0))
                longitude = float(data.get("places", [{}])[0].get("longitude", 0))

                # Calculate direction from New York
                direction = self.calculate_direction(latitude, longitude)

                return {
                    "latitude": latitude,
                    "longitude": longitude,
                    "direction_from_new_york": direction
                }
        except httpx.RequestError as e:
            logger.error(f"HTTP request failed: {str(e)}")
            raise ExternalServiceError(
                message=f"Error connecting to location service: {str(e)}",
                details={"postcode": postcode}
            )

    def calculate_direction(self, latitude: float, longitude: float) -> str:
        """Calculate direction from New York based on coordinates."""
        ny_lat = config.NEW_YORK_LAT
        ny_lon = config.NEW_YORK_LON

        is_north = latitude >= ny_lat
        is_east = longitude >= ny_lon

        if is_north and is_east:
            return Direction.NE.value
        elif is_north and not is_east:
            return Direction.NW.value
        elif not is_north and is_east:
            return Direction.SE.value
        else:
            return Direction.SW.value

class ItemService(ItemServiceInterface):
    """Implementation of the item service"""

    def __init__(
        self,
        geo_service: GeoLocationService = None,
        event_emitter: EventEmitter = event_emitter,
        validator: ItemValidator = item_validator
    ):
        self.geo_service = geo_service or DefaultGeoLocationService()
        self.event_emitter = event_emitter
        self.validator = validator

    async def get_all_items(self) -> List[Item]:
        return Item.objects.all()

    async def get_item_by_id(self, item_id: str) -> Item:
        item = Item.objects(id=item_id).first()
        if not item:
            raise NotFoundError(f"Item with id {item_id} not found")
        return item

    async def create_item(self, data: ItemCreate) -> Item:
        # Validate input data
        self.validator.validate_create(data)

        # Create a new item
        item_data = data.dict()

        # Ensure start_date is timezone aware
        if item_data['start_date'].tzinfo is None:
            item_data['start_date'] = item_data['start_date'].replace(tzinfo=timezone.utc)

        # Get location data
        try:
            geo_data = await self.geo_service.get_location_data(data.postcode)
            item_data.update(geo_data)
        except Exception as e:
            logger.error(f"Error fetching location data: {str(e)}")
            # Continue with creation, but without geo data
            item_data.update({
                "latitude": None,
                "longitude": None,
                "direction_from_new_york": None
            })

        # Create the item
        item = Item(**item_data)
        item.save()

        # Emit item created event
        self.event_emitter.emit("item.created", {"item_id": str(item.id)})

        return item

    async def update_item(self, item_id: str, data: ItemUpdate) -> Item:
        item = await self.get_item_by_id(item_id)
        item_dict = item.to_dict()

        # Only update mutable fields
        update_data = {}
        if data.name is not None:
            update_data["name"] = data.name
        if data.title is not None:
            update_data["title"] = data.title
        if data.users is not None:
            update_data["users"] = data.users
        if data.start_date is not None:
            update_data["start_date"] = data.start_date

        # Validate update data
        self.validator.validate_update(item_dict, update_data)

        # Update the item
        for key, value in update_data.items():
            setattr(item, key, value)

        item.save()

        # Emit item updated event
        self.event_emitter.emit("item.updated", {"item_id": str(item.id)})

        return item

    async def delete_item(self, item_id: str) -> bool:
        item = await self.get_item_by_id(item_id)
        item.delete()

        # Emit item deleted event
        self.event_emitter.emit("item.deleted", {"item_id": item_id})

        return True

# Create default instance for backward compatibility
item_service = ItemService()
