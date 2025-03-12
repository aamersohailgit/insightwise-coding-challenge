import asyncio
import json
import time
from datetime import datetime, timedelta

from app.core.logging_config import get_logger
from app.services.geo_service import GeoService
from app.repositories.item_repository import ItemRepository
from app.utils.api_error_handler import ApiError

logger = get_logger(__name__)

"""
This module demonstrates how you could implement a worker to process
geo lookup retries. In a production environment, you'd use a proper task queue
like Celery or Redis-based queue with worker processes.
"""

class GeoWorker:
    """Worker that processes failed geo lookups."""

    def __init__(self, polling_interval=60):
        """
        Initialize the geo worker.

        Args:
            polling_interval: Seconds between checks for new items to process
        """
        self.polling_interval = polling_interval
        self.running = False

    async def start(self):
        """Start the worker process."""
        logger.info("Starting Geo Worker")
        self.running = True

        while self.running:
            try:
                # Process any pending lookups
                await self.process_pending_lookups()

                # Wait for next polling interval
                await asyncio.sleep(self.polling_interval)
            except Exception as e:
                logger.exception(f"Error in geo worker loop: {str(e)}")
                await asyncio.sleep(self.polling_interval)

    async def stop(self):
        """Stop the worker process."""
        logger.info("Stopping Geo Worker")
        self.running = False

    async def process_pending_lookups(self):
        """Process pending geo lookups from the retry queue."""
        # In a real implementation, you would fetch from your queue system
        # e.g., items = await redis_client.lrange('geo_lookup_retry_queue', 0, 10)

        # Mock implementation
        mock_items = self._get_mock_retry_items()

        if not mock_items:
            logger.debug("No pending geo lookups to process")
            return

        logger.info(f"Processing {len(mock_items)} pending geo lookups")

        for item in mock_items:
            await self._process_lookup(item)

    async def _process_lookup(self, queue_item):
        """Process a single lookup item from the queue."""
        try:
            # Extract data
            postcode = queue_item.get('postcode')
            item_id = queue_item.get('item_id')

            logger.info(f"Retrying geo lookup for postcode: {postcode}",
                       extra={"postcode": postcode, "item_id": item_id})

            # Skip items that have been retried too many times
            retry_count = queue_item.get('retry_count', 0)
            if retry_count >= 5:
                logger.warning(f"Max retries exceeded for postcode {postcode}, giving up",
                              extra={"postcode": postcode, "retry_count": retry_count})
                # Remove from queue
                # await redis_client.lrem('geo_lookup_retry_queue', 1, json.dumps(queue_item))
                return

            # Attempt to get coordinates
            geo_data = await GeoService.get_coordinates(postcode)

            if not geo_data:
                logger.warning(f"Still no geo data available for postcode: {postcode}",
                              extra={"postcode": postcode})

                # Increment retry count and push back to queue
                queue_item['retry_count'] = retry_count + 1
                queue_item['next_retry'] = (datetime.utcnow() + timedelta(minutes=30)).isoformat()
                # await redis_client.lpush('geo_lookup_retry_queue', json.dumps(queue_item))
                return

            # If we have item_id, update its geo data
            if item_id:
                logger.info(f"Updating geo data for item: {item_id}",
                           extra={"item_id": item_id, "postcode": postcode})
                await ItemRepository.update_geo_data(item_id, geo_data)

            # Remove from queue on success
            # await redis_client.lrem('geo_lookup_retry_queue', 1, json.dumps(queue_item))

            logger.info(f"Successfully processed geo lookup for postcode: {postcode}",
                       extra={"postcode": postcode})

        except ApiError as e:
            logger.error(f"API error during retry for postcode {postcode}: {str(e)}",
                        extra={"postcode": postcode, "error": str(e)})

            # Increment retry count and adjust next retry time
            queue_item['retry_count'] = queue_item.get('retry_count', 0) + 1
            queue_item['last_error'] = str(e)
            queue_item['next_retry'] = (datetime.utcnow() + timedelta(hours=1)).isoformat()
            # await redis_client.lpush('geo_lookup_retry_queue', json.dumps(queue_item))

        except Exception as e:
            logger.exception(f"Unexpected error processing geo lookup for {postcode}",
                            extra={"postcode": postcode})

            # Increment retry count
            queue_item['retry_count'] = queue_item.get('retry_count', 0) + 1
            queue_item['last_error'] = str(e)
            queue_item['next_retry'] = (datetime.utcnow() + timedelta(minutes=15)).isoformat()
            # await redis_client.lpush('geo_lookup_retry_queue', json.dumps(queue_item))

    def _get_mock_retry_items(self):
        """Simulate getting items from a queue (for demonstration only)."""
        # In reality, this would come from Redis, RabbitMQ, etc.
        return []

# Singleton instance
geo_worker = GeoWorker()

# For manual testing
if __name__ == "__main__":
    async def main():
        try:
            await geo_worker.start()
        except KeyboardInterrupt:
            await geo_worker.stop()

    asyncio.run(main())