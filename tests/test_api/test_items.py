from datetime import datetime, timedelta, timezone
from unittest.mock import patch, AsyncMock
import pytest

from app.features.items.models import Item
from app.schemas.item import ItemCreate, ItemUpdate
from fastapi.encoders import jsonable_encoder


@pytest.fixture
def valid_item_data():
    """Return valid item data for testing."""
    # Start date must be 1 week in the future
    start_date = (datetime.utcnow() + timedelta(days=10)).isoformat()

    return {
        "name": "Test Item",
        "postcode": "10001",
        "title": "Test Title",
        "users": ["Test Item", "Another User"],
        "startDate": start_date
    }

def test_create_item(client, valid_item_data):
    """Test creating an item."""
    response = client.post("/api/v1/items", json=valid_item_data)
    assert response.status_code == 201

    data = response.json()
    assert data["name"] == valid_item_data["name"]
    assert data["postcode"] == valid_item_data["postcode"]
    assert data["title"] == valid_item_data["title"]
    assert data["id"] is not None
    assert "latitude" in data
    assert "longitude" in data
    assert "directionFromNewYork" in data

def test_get_items(client, valid_item_data):
    """Test getting items list."""
    # First create an item
    client.post("/api/v1/items", json=valid_item_data)

    # Now get items list
    response = client.get("/api/v1/items")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_get_item_by_id(client, valid_item_data):
    """Test getting a specific item by ID."""
    # First create an item
    create_response = client.post("/api/v1/items", json=valid_item_data)
    item_id = create_response.json()["id"]

    # Now get the specific item
    response = client.get(f"/api/v1/items/{item_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == item_id
    assert data["name"] == valid_item_data["name"]

def test_update_item(client, valid_item_data):
    """Test updating an item."""
    # First create an item
    create_response = client.post("/api/v1/items", json=valid_item_data)
    item_id = create_response.json()["id"]

    # Update the item
    update_data = {
        "title": "Updated Title"
    }
    response = client.patch(f"/api/v1/items/{item_id}", json=update_data)
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == item_id
    assert data["title"] == update_data["title"]
    assert data["name"] == valid_item_data["name"]  # other fields unchanged

def test_delete_item(client, valid_item_data):
    """Test deleting an item."""
    # First create an item
    create_response = client.post("/api/v1/items", json=valid_item_data)
    item_id = create_response.json()["id"]

    # Delete the item
    response = client.delete(f"/api/v1/items/{item_id}")
    assert response.status_code == 204

    # Verify it's deleted
    get_response = client.get(f"/api/v1/items/{item_id}")
    assert get_response.status_code == 404

def test_create_item_success(client, auth_headers):
    """Test creating an item successfully."""
    # Create valid item data using schema
    start_date = datetime.utcnow() + timedelta(days=10)
    if start_date.tzinfo is None:
        start_date = start_date.replace(tzinfo=timezone.utc)

    item_data = ItemCreate(
        name="Test Item",
        postcode="12345",
        title="Test Title",
        users=["Test Item", "User 1"],
        startDate=start_date
    )

    # Mock the geo service
    geo_data = {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "direction_from_new_york": "SW"
    }

    with patch('app.services.geo_service.GeoService.get_coordinates',
               new_callable=AsyncMock, return_value=geo_data):
        # Use jsonable_encoder instead of dict() to handle datetime serialization
        response = client.post(
            "/items",
            json=jsonable_encoder(item_data),
            headers=auth_headers
        )

        # Verify response
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == item_data.name
        assert data["postcode"] == item_data.postcode
        assert data["title"] == item_data.title
        assert "latitude" in data
        assert "longitude" in data
        assert "directionFromNewYork" in data


def test_create_item_validation_error(client, auth_headers):
    """Test validation error when creating an item."""
    # Use past date (invalid)
    past_date = datetime.utcnow() - timedelta(days=1)
    if past_date.tzinfo is None:
        past_date = past_date.replace(tzinfo=timezone.utc)

    # Create invalid item data that will fail validation
    invalid_data = {
        "name": "Test Item",
        "postcode": "12345",
        "title": "Test Title",
        "users": ["Test Item"],
        "startDate": past_date.isoformat()  # This will fail validation
    }

    # Make request
    response = client.post(
        "/items",
        json=invalid_data,
        headers=auth_headers
    )

    # Verify response indicates validation error
    assert response.status_code == 422
    assert "detail" in response.json()


def test_get_all_items(client, auth_headers):
    """Test getting all items."""
    # Clean database and add test items
    Item.objects.delete()

    start_date = datetime.utcnow() + timedelta(days=10)
    if start_date.tzinfo is None:
        start_date = start_date.replace(tzinfo=timezone.utc)

    Item(
        name="Item 1",
        postcode="12345",
        users=["Item 1"],
        start_date=start_date
    ).save()

    Item(
        name="Item 2",
        postcode="67890",
        users=["Item 2"],
        start_date=start_date
    ).save()

    # Make request
    response = client.get("/items", headers=auth_headers)

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert any(item["name"] == "Item 1" for item in data)
    assert any(item["name"] == "Item 2" for item in data)


def test_update_item(client, auth_headers):
    """Test updating an item."""
    # Clean database and add test item
    Item.objects.delete()

    start_date = datetime.utcnow() + timedelta(days=10)
    if start_date.tzinfo is None:
        start_date = start_date.replace(tzinfo=timezone.utc)

    item = Item(
        name="Test Item",
        postcode="12345",
        title="Old Title",
        users=["Test Item"],
        start_date=start_date
    ).save()

    # Create update data using schema
    update_data = ItemUpdate(
        title="New Title"
    )

    # Make request (exclude_unset=True ensures only set fields are included)
    response = client.patch(
        f"/items/{item.id}",
        json=update_data.dict(exclude_unset=True),
        headers=auth_headers
    )

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Title"


def test_delete_item(client, auth_headers):
    """Test deleting an item."""
    # Clean database and add test item
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

    # Make request
    response = client.delete(f"/items/{item.id}", headers=auth_headers)

    # Verify response
    assert response.status_code == 204

    # Verify item was deleted
    assert Item.objects.filter(id=item.id).count() == 0