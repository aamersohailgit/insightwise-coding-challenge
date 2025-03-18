import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock, AsyncMock
import time
from collections import OrderedDict

from fastapi.testclient import TestClient
from app.main import app
from app.core.events import event_emitter as real_event_emitter

@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)

@pytest.fixture
def future_start_date():
    """Create a future start date for testing"""
    return (datetime.now(timezone.utc) + timedelta(days=10)).isoformat()

@pytest.fixture
def valid_item_data(future_start_date):
    """Create valid item data for testing"""
    item_name = "Test Event Item"
    return {
        "name": item_name,
        "postcode": "10001",
        "title": "Test Title",
        "users": [item_name, "Another User"],
        "start_date": future_start_date
    }

@pytest.fixture
def mock_event_emitter():
    """Mock the event emitter to capture emitted events"""
    mock_emitter = MagicMock()
    mock_emitter.emit = MagicMock()
    return mock_emitter

def test_create_item_emits_event(client, valid_item_data):
    """Test that creating an item emits the expected event"""
    # Patch the event emitter directly
    original_emit = real_event_emitter.emit
    mock_emit = MagicMock()
    real_event_emitter.emit = mock_emit

    try:
        # Create an item
        response = client.post("/api/v1/items/", json=valid_item_data)

        # Check the response
        assert response.status_code == 201
        item_id = response.json()["id"]

        # Allow some time for the event to be processed
        time.sleep(0.1)

        # Verify the event was emitted
        mock_emit.assert_called_with("item.created", {"item_id": item_id})
    finally:
        # Restore the original emit function
        real_event_emitter.emit = original_emit

def test_update_item_emits_event(client, valid_item_data):
    """Test that updating an item emits the expected event"""
    # First create an item
    create_response = client.post("/api/v1/items/", json=valid_item_data)
    assert create_response.status_code == 201
    item_id = create_response.json()["id"]

    # Patch the event emitter directly
    original_emit = real_event_emitter.emit
    mock_emit = MagicMock()
    real_event_emitter.emit = mock_emit

    try:
        # Update the item
        update_data = {"title": "Updated Title"}
        update_response = client.patch(f"/api/v1/items/{item_id}", json=update_data)

        # Check the response
        assert update_response.status_code == 200

        # Allow some time for the event to be processed
        time.sleep(0.1)

        # Verify the event was emitted
        mock_emit.assert_called_with("item.updated", {"item_id": item_id})
    finally:
        # Restore the original emit function
        real_event_emitter.emit = original_emit

def test_delete_item_emits_event(client, valid_item_data):
    """Test that deleting an item emits the expected event"""
    # First create an item
    create_response = client.post("/api/v1/items/", json=valid_item_data)
    assert create_response.status_code == 201
    item_id = create_response.json()["id"]

    # Patch the event emitter directly
    original_emit = real_event_emitter.emit
    mock_emit = MagicMock()
    real_event_emitter.emit = mock_emit

    try:
        # Delete the item
        delete_response = client.delete(f"/api/v1/items/{item_id}")

        # Check the response
        assert delete_response.status_code == 204

        # Allow some time for the event to be processed
        time.sleep(0.1)

        # Verify the event was emitted
        mock_emit.assert_called_with("item.deleted", {"item_id": item_id})
    finally:
        # Restore the original emit function
        real_event_emitter.emit = original_emit

def test_event_handler_processes_created_event(client, valid_item_data):
    """Test that the event handler processes item.created events correctly"""
    # Create a mock handler
    mock_handler = MagicMock()

    # Add our mock handler to the event emitter
    listener = real_event_emitter.on('item.created', mock_handler)

    try:
        # Create an item (which should emit an event)
        response = client.post("/api/v1/items/", json=valid_item_data)

        # Check the response
        assert response.status_code == 201

        # Allow some time for the event to be processed
        time.sleep(0.1)

        # Verify the handler was called
        assert mock_handler.call_count > 0
    finally:
        # Remove our handler - need to use the proper remove_listener method
        real_event_emitter.remove_listener('item.created', mock_handler)

def test_event_handler_processes_updated_event(client, valid_item_data):
    """Test that the event handler processes item.updated events correctly"""
    # First create an item
    create_response = client.post("/api/v1/items/", json=valid_item_data)
    assert create_response.status_code == 201
    item_id = create_response.json()["id"]

    # Create a mock handler
    mock_handler = MagicMock()

    # Add our mock handler to the event emitter
    listener = real_event_emitter.on('item.updated', mock_handler)

    try:
        # Update the item
        update_data = {"title": "Updated Title"}
        update_response = client.patch(f"/api/v1/items/{item_id}", json=update_data)

        # Check the response
        assert update_response.status_code == 200

        # Allow some time for the event to be processed
        time.sleep(0.1)

        # Verify the handler was called
        assert mock_handler.call_count > 0
    finally:
        # Remove our handler - need to use the proper remove_listener method
        real_event_emitter.remove_listener('item.updated', mock_handler)

def test_event_handler_processes_deleted_event(client, valid_item_data):
    """Test that the event handler processes item.deleted events correctly"""
    # First create an item
    create_response = client.post("/api/v1/items/", json=valid_item_data)
    assert create_response.status_code == 201
    item_id = create_response.json()["id"]

    # Create a mock handler
    mock_handler = MagicMock()

    # Add our mock handler to the event emitter
    listener = real_event_emitter.on('item.deleted', mock_handler)

    try:
        # Delete the item
        delete_response = client.delete(f"/api/v1/items/{item_id}")

        # Check the response
        assert delete_response.status_code == 204

        # Allow some time for the event to be processed
        time.sleep(0.1)

        # Verify the handler was called
        assert mock_handler.call_count > 0
    finally:
        # Remove our handler - need to use the proper remove_listener method
        real_event_emitter.remove_listener('item.deleted', mock_handler)