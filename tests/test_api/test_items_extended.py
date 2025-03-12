import json
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, AsyncMock

import pytest
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException

from app.models.item import Item


def test_get_item_not_found(client, auth_headers):
    """Test getting a non-existent item returns 404."""
    # Use a nonexistent ID
    non_existent_id = "000000000000000000000000"

    # Make request
    response = client.get(f"/items/{non_existent_id}", headers=auth_headers)

    # Verify response
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


def test_update_item_not_found(client, auth_headers):
    """Test updating a non-existent item returns 404."""
    # Use a nonexistent ID
    non_existent_id = "000000000000000000000000"

    # Make request with valid update data
    response = client.patch(
        f"/items/{non_existent_id}",
        json={"title": "New Title"},
        headers=auth_headers
    )

    # Verify response
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


def test_update_item_validation_error(client, auth_headers):
    """Test validation error when updating an item."""
    # Create a test item
    Item.objects.delete()

    start_date = datetime.utcnow() + timedelta(days=10)
    if start_date.tzinfo is None:
        start_date = start_date.replace(tzinfo=timezone.utc)

    item = Item(
        name="Test Item",
        postcode="12345",
        title="Test Title",
        users=["Test Item"],
        start_date=start_date
    ).save()

    # New start date is in the past (invalid)
    past_date = datetime.utcnow() - timedelta(days=1)
    if past_date.tzinfo is None:
        past_date = past_date.replace(tzinfo=timezone.utc)

    # Make request with invalid update data
    response = client.patch(
        f"/items/{item.id}",
        json={"startDate": past_date.isoformat()},
        headers=auth_headers
    )

    # Verify response
    assert response.status_code == 422
    assert "detail" in response.json()


def test_delete_item_not_found(client, auth_headers):
    """Test deleting a non-existent item returns 404."""
    # Use a nonexistent ID
    non_existent_id = "000000000000000000000000"

    # Make request
    response = client.delete(f"/items/{non_existent_id}", headers=auth_headers)

    # Verify response
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


def test_create_item_internal_error(client, auth_headers):
    """Test handling of internal errors during item creation."""
    # Create valid item data
    start_date = datetime.utcnow() + timedelta(days=10)
    if start_date.tzinfo is None:
        start_date = start_date.replace(tzinfo=timezone.utc)

    item_data = {
        "name": "Test Item",
        "postcode": "12345",
        "title": "Test Title",
        "users": ["Test Item"],
        "startDate": start_date.isoformat()
    }

    # Patch the service to raise an exception
    with patch('app.services.item_service.ItemService.create_item',
              AsyncMock(side_effect=Exception("Database error"))):
        # Make request
        response = client.post(
            "/items",
            json=item_data,
            headers=auth_headers
        )

        # Verify response
        assert response.status_code == 500
        assert response.json()["detail"] == "Internal server error"


def test_update_item_internal_error(client, auth_headers):
    """Test handling of internal errors during item update."""
    # Create a test item
    Item.objects.delete()

    start_date = datetime.utcnow() + timedelta(days=10)
    if start_date.tzinfo is None:
        start_date = start_date.replace(tzinfo=timezone.utc)

    item = Item(
        name="Test Item",
        postcode="12345",
        title="Test Title",
        users=["Test Item"],
        start_date=start_date
    ).save()

    # Patch the service to raise an exception
    with patch('app.services.item_service.ItemService.update_item',
              AsyncMock(side_effect=Exception("Database error"))):
        # Make request
        response = client.patch(
            f"/items/{item.id}",
            json={"title": "New Title"},
            headers=auth_headers
        )

        # Verify response
        assert response.status_code == 500
        assert response.json()["detail"] == "Internal server error"


def test_get_all_items_internal_error(client, auth_headers):
    """Test handling of internal errors when getting all items."""
    # Patch the service to raise an exception
    with patch('app.services.item_service.ItemService.get_all_items',
              AsyncMock(side_effect=Exception("Database error"))):
        # Make request
        response = client.get("/items", headers=auth_headers)

        # Verify response
        assert response.status_code == 500
        assert response.json()["detail"] == "Internal server error"


def test_get_item_internal_error(client, auth_headers):
    """Test handling of internal errors when getting a specific item."""
    # Create a test item
    Item.objects.delete()

    start_date = datetime.utcnow() + timedelta(days=10)
    if start_date.tzinfo is None:
        start_date = start_date.replace(tzinfo=timezone.utc)

    item = Item(
        name="Test Item",
        postcode="12345",
        title="Test Title",
        users=["Test Item"],
        start_date=start_date
    ).save()

    # Patch the service to raise an exception
    with patch('app.services.item_service.ItemService.get_item',
              AsyncMock(side_effect=Exception("Database error"))):
        # Make request
        response = client.get(f"/items/{item.id}", headers=auth_headers)

        # Verify response
        assert response.status_code == 500
        assert response.json()["detail"] == "Internal server error"


def test_delete_item_internal_error(client, auth_headers):
    """Test handling of internal errors when deleting an item."""
    # Create a test item
    Item.objects.delete()

    start_date = datetime.utcnow() + timedelta(days=10)
    if start_date.tzinfo is None:
        start_date = start_date.replace(tzinfo=timezone.utc)

    item = Item(
        name="Test Item",
        postcode="12345",
        title="Test Title",
        users=["Test Item"],
        start_date=start_date
    ).save()

    # Patch the service to raise an exception
    with patch('app.services.item_service.ItemService.delete_item',
              AsyncMock(side_effect=Exception("Database error"))):
        # Make request
        response = client.delete(f"/items/{item.id}", headers=auth_headers)

        # Verify response
        assert response.status_code == 500
        assert response.json()["detail"] == "Internal server error"