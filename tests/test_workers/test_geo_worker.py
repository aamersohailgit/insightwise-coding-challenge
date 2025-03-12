import asyncio
import json
from datetime import datetime, timedelta
import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from app.workers.geo_worker import GeoWorker
from app.utils.api_error_handler import ApiError

@pytest.fixture
def geo_worker():
    """Create a GeoWorker instance with a short polling interval for testing."""
    worker = GeoWorker(polling_interval=0.1)
    return worker

async def test_worker_start_stop(geo_worker):
    """Test that the worker can start and stop correctly."""
    # Patch the process_pending_lookups method to avoid actual processing
    with patch.object(geo_worker, 'process_pending_lookups', AsyncMock()) as mock_process:
        # Start the worker in a task
        task = asyncio.create_task(geo_worker.start())

        # Wait a short time to ensure the worker has started
        await asyncio.sleep(0.2)

        # Check that the worker is running and has called process_pending_lookups
        assert geo_worker.running is True
        assert mock_process.called

        # Stop the worker
        await geo_worker.stop()

        # Wait for the task to complete
        try:
            # Add a timeout to avoid hanging if stop doesn't work
            await asyncio.wait_for(task, timeout=0.3)
        except asyncio.TimeoutError:
            # Cancel the task if it doesn't complete
            task.cancel()

        # Verify the worker is stopped
        assert geo_worker.running is False

async def test_process_pending_lookups_empty(geo_worker):
    """Test processing when no items are in the queue."""
    # Mock _get_mock_retry_items to return empty list
    with patch.object(geo_worker, '_get_mock_retry_items', return_value=[]):
        # This should execute without error
        await geo_worker.process_pending_lookups()

async def test_process_pending_lookups_with_items(geo_worker):
    """Test processing items from the queue."""
    # Create some mock items
    mock_items = [
        {"postcode": "12345", "item_id": "item1", "retry_count": 0},
        {"postcode": "67890", "item_id": "item2", "retry_count": 1}
    ]

    # Mock the _get_mock_retry_items method
    with patch.object(geo_worker, '_get_mock_retry_items', return_value=mock_items), \
         patch.object(geo_worker, '_process_lookup', AsyncMock()) as mock_process:

        # Process the lookups
        await geo_worker.process_pending_lookups()

        # Verify each item was processed
        assert mock_process.call_count == 2
        mock_process.assert_any_call(mock_items[0])
        mock_process.assert_any_call(mock_items[1])

async def test_process_lookup_success(geo_worker):
    """Test successful processing of a lookup item."""
    # Mock data
    item = {"postcode": "12345", "item_id": "item1", "retry_count": 0}
    geo_data = {"latitude": 40.7128, "longitude": -74.0060}

    # Mock dependencies
    with patch('app.services.geo_service.GeoService.get_coordinates', AsyncMock(return_value=geo_data)), \
         patch('app.repositories.item_repository.ItemRepository.update_geo_data', AsyncMock()) as mock_update:

        # Process the lookup
        await geo_worker._process_lookup(item)

        # Verify the item was updated with geo data
        mock_update.assert_called_once_with("item1", geo_data)

async def test_process_lookup_max_retries(geo_worker):
    """Test that items with too many retries are skipped."""
    # Mock data with high retry count
    item = {"postcode": "12345", "item_id": "item1", "retry_count": 5}

    # Mock dependencies to ensure they're not called
    with patch('app.services.geo_service.GeoService.get_coordinates', AsyncMock()) as mock_get_coords, \
         patch('app.repositories.item_repository.ItemRepository.update_geo_data', AsyncMock()) as mock_update:

        # Process the lookup
        await geo_worker._process_lookup(item)

        # Verify no calls were made
        mock_get_coords.assert_not_called()
        mock_update.assert_not_called()

async def test_process_lookup_no_geo_data(geo_worker):
    """Test handling when geo service returns no data."""
    # Mock data
    item = {"postcode": "12345", "item_id": "item1", "retry_count": 0}

    # Mock dependencies
    with patch('app.services.geo_service.GeoService.get_coordinates', AsyncMock(return_value=None)), \
         patch('app.repositories.item_repository.ItemRepository.update_geo_data', AsyncMock()) as mock_update:

        # Process the lookup
        await geo_worker._process_lookup(item)

        # Verify update was not called
        mock_update.assert_not_called()
        # Verify retry count was incremented
        assert item["retry_count"] == 1
        assert "next_retry" in item

async def test_process_lookup_api_error(geo_worker):
    """Test handling of API errors."""
    # Mock data
    item = {"postcode": "12345", "item_id": "item1", "retry_count": 0}

    # Mock dependencies with error
    with patch('app.services.geo_service.GeoService.get_coordinates',
               AsyncMock(side_effect=ApiError("API Error", status_code=500))):

        # Process the lookup
        await geo_worker._process_lookup(item)

        # Verify error handling
        assert item["retry_count"] == 1
        assert "last_error" in item
        assert "next_retry" in item

async def test_process_lookup_unexpected_error(geo_worker):
    """Test handling of unexpected errors."""
    # Mock data
    item = {"postcode": "12345", "item_id": "item1", "retry_count": 0}

    # Mock dependencies with error
    with patch('app.services.geo_service.GeoService.get_coordinates',
               AsyncMock(side_effect=Exception("Unexpected error"))):

        # Process the lookup
        await geo_worker._process_lookup(item)

        # Verify error handling
        assert item["retry_count"] == 1
        assert "last_error" in item
        assert "next_retry" in item