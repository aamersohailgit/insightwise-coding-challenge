import logging
from typing import Dict, Any

from pyee import EventEmitter

from app.core.logging_config import get_logger

logger = get_logger(__name__)

event_emitter = EventEmitter()

@event_emitter.on('item.created')
def handle_item_created(item_id: str, item_data: Dict[str, Any]):
    """Handle item creation event."""
    logger.info(f"Event: Item created: {item_id}", extra={"item_id": item_id})

@event_emitter.on('item.updated')
def handle_item_updated(item_id: str, updates: Dict[str, Any]):
    """Handle item update event."""
    logger.info(f"Event: Item updated: {item_id}", extra={"item_id": item_id, "fields_updated": list(updates.keys())})

@event_emitter.on('item.deleted')
def handle_item_deleted(item_id: str):
    """Handle item deletion event."""
    logger.info(f"Event: Item deleted: {item_id}", extra={"item_id": item_id})

@event_emitter.on('geo.lookup')
def handle_geo_lookup(item_id: str, postcode: str):
    """Handle geolocation lookup event."""
    logger.info(f"Event: Geo lookup for item {item_id} with postcode {postcode}",
               extra={"item_id": item_id, "postcode": postcode})

@event_emitter.on('geo.lookup.success')
def handle_geo_lookup_success(postcode: str, data: Dict[str, Any]):
    """Handle successful geolocation lookup."""
    logger.info(f"Event: Geo lookup success for postcode {postcode}",
               extra={"postcode": postcode, "geo_data": data})

@event_emitter.on('geo.lookup.error')
def handle_geo_lookup_error(postcode: str, error: str):
    """Handle geolocation lookup error."""
    logger.error(f"Event: Geo lookup error for postcode {postcode}: {error}",
                extra={"postcode": postcode, "error": error})
    # You could implement recovery logic here, such as:
    # 1. Add to a retry queue
    # 2. Send notification to admin
    # 3. Log to a special error tracking system
    add_to_retry_queue(postcode, error)

# API error events
@event_emitter.on('api.geo_lookup.error')
def handle_api_error(status_code=None, error=None):
    """Handle API error events."""
    logger.error(f"API Error during geo lookup: {error}",
                extra={"status_code": status_code, "error": error})
    # Could trigger alerts or monitoring

@event_emitter.on('api.geo_lookup.connection_error')
def handle_connection_error(error=None):
    """Handle API connection error events."""
    logger.error(f"API Connection Error during geo lookup: {error}",
                extra={"error": error})
    # Could check service health or trigger circuit breaker

# Mock implementation of recovery mechanisms
def add_to_retry_queue(postcode: str, error: str):
    """
    Add a failed geo lookup to a retry queue.

    In a production application, this would use a proper task queue
    like Celery, Redis, or a message broker.
    """
    logger.info(f"Added postcode {postcode} to retry queue due to error: {error}",
               extra={"postcode": postcode, "error": error})
    # TODO: Implement actual queue mechanism
    # Example implementation might look like:
    # redis_client.lpush('geo_lookup_retry_queue', json.dumps({
    #     'postcode': postcode,
    #     'error': error,
    #     'timestamp': datetime.utcnow().isoformat()
    # }))