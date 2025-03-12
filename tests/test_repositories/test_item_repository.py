import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from bson import ObjectId

from app.models.item import Item
from app.repositories.item_repository import ItemRepository


@pytest.mark.asyncio
async def test_create_item():
    Item.objects.delete()

    start_date = datetime.utcnow() + timedelta(days=10)
    if start_date.tzinfo is None:
        start_date = start_date.replace(tzinfo=timezone.utc)

    item_data = {
        "name": "Test Item",
        "postcode": "12345",
        "title": "Test Title",
        "users": ["Test Item", "User 1"],
        "start_date": start_date
    }

    with patch('app.core.events.event_emitter.emit') as mock_emit:
        item = await ItemRepository.create_item(item_data)

        assert item is not None
        assert item.name == "Test Item"
        assert item.postcode == "12345"
        assert item.title == "Test Title"

        mock_emit.assert_called_once()


@pytest.mark.asyncio
async def test_get_item_by_id():
    Item.objects.delete()

    start_date = datetime.utcnow() + timedelta(days=10)
    if start_date.tzinfo is None:
        start_date = start_date.replace(tzinfo=timezone.utc)

    item = Item(
        name="Test Item",
        postcode="12345",
        title="Test Title",
        users=["Test Item", "User 1"],
        start_date=start_date
    ).save()

    result = await ItemRepository.get_item_by_id(str(item.id))

    assert result is not None
    assert str(result.id) == str(item.id)
    assert result.name == "Test Item"


@pytest.mark.asyncio
async def test_get_item_not_found():
    result = await ItemRepository.get_item_by_id("non-existent-id")

    assert result is None


@pytest.mark.asyncio
async def test_get_all_items():
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

    results = await ItemRepository.get_all_items()

    assert len(results) == 2
    assert any(item.name == "Item 1" for item in results)
    assert any(item.name == "Item 2" for item in results)


@pytest.mark.asyncio
async def test_update_item():
    Item.objects.delete()

    start_date = datetime.utcnow() + timedelta(days=10)
    if start_date.tzinfo is None:
        start_date = start_date.replace(tzinfo=timezone.utc)

    item = Item(
        name="Test Item",
        postcode="12345",
        title="Old Title",
        users=["Test Item", "User 1"],
        start_date=start_date
    ).save()

    update_data = {
        "title": "New Title"
    }

    with patch('app.core.events.event_emitter.emit') as mock_emit:
        result = await ItemRepository.update_item(str(item.id), update_data)

        assert result is not None
        assert result.title == "New Title"

        mock_emit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_item():
    Item.objects.delete()

    start_date = datetime.utcnow() + timedelta(days=10)
    if start_date.tzinfo is None:
        start_date = start_date.replace(tzinfo=timezone.utc)

    item = Item(
        name="Test Item",
        postcode="12345",
        title="Test Title",
        users=["Test Item", "User 1"],
        start_date=start_date
    ).save()

    with patch('app.core.events.event_emitter.emit') as mock_emit:
        result = await ItemRepository.delete_item(str(item.id))

        assert result is True
        assert await ItemRepository.get_item_by_id(str(item.id)) is None

        mock_emit.assert_called_once()


@pytest.mark.asyncio
async def test_update_geo_data():
    Item.objects.delete()

    start_date = datetime.utcnow() + timedelta(days=10)
    if start_date.tzinfo is None:
        start_date = start_date.replace(tzinfo=timezone.utc)

    item = Item(
        name="Test Item",
        postcode="12345",
        title="Test Title",
        users=["Test Item", "User 1"],
        start_date=start_date
    ).save()

    geo_data = {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "direction_from_new_york": "SE"
    }

    result = await ItemRepository.update_geo_data(str(item.id), geo_data)

    assert result is not None
    assert result.latitude == geo_data["latitude"]
    assert result.longitude == geo_data["longitude"]
    assert result.direction_from_new_york == geo_data["direction_from_new_york"]