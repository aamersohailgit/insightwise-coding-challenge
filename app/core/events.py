import logging
from typing import Dict, Any

from pyee import EventEmitter

logger = logging.getLogger(__name__)

event_emitter = EventEmitter()

@event_emitter.on('item.created')
def handle_item_created(item_id: str, item_data: Dict[str, Any]):
    """Handle item creation event."""
    logger.info(f"Event: Item created: {item_id}")

@event_emitter.on('item.updated')
def handle_item_updated(item_id: str, updates: Dict[str, Any]):
    """Handle item update event."""
    logger.info(f"Event: Item updated: {item_id}")

@event_emitter.on('item.deleted')
def handle_item_deleted(item_id: str):
    """Handle item deletion event."""
    logger.info(f"Event: Item deleted: {item_id}")

@event_emitter.on('geo.lookup')
def handle_geo_lookup(item_id: str, postcode: str):
    """Handle geolocation lookup event."""
    logger.info(f"Event: Geo lookup for item {item_id} with postcode {postcode}")

@event_emitter.on('geo.lookup.success')
def handle_geo_lookup_success(item_id: str, data: Dict[str, Any]):
    """Handle successful geolocation lookup."""
    logger.info(f"Event: Geo lookup success for item {item_id}")

@event_emitter.on('geo.lookup.error')
def handle_geo_lookup_error(item_id: str, error: str):
    """Handle geolocation lookup error."""
    logger.error(f"Event: Geo lookup error for item {item_id}: {error}")