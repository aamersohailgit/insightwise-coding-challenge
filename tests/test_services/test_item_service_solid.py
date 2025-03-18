import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timedelta, timezone

from app.features.items.models import Item, Direction
from app.features.items.schemas import ItemCreate, ItemUpdate
from app.features.items.service import (
    ItemService,
    DefaultGeoLocationService,
    ItemServiceInterface
)
from app.utils.errors import NotFoundError, ValidationError, ExternalServiceError

@pytest.fixture
def mock_geo_service():
    """Mock geo location service"""
    mock = AsyncMock()
    mock.get_location_data.return_value = {
        "latitude": 40.7484,
        "longitude": -73.9967,
        "direction_from_new_york": Direction.SE.value
    }
    mock.calculate_direction.return_value = Direction.SE.value
    return mock

@pytest.fixture
def mock_event_emitter():
    """Mock event emitter"""
    mock = MagicMock()
    mock.emit.return_value = None
    return mock

@pytest.fixture
def mock_validator():
    """Mock item validator"""
    mock = MagicMock()
    mock.validate_create.return_value = None
    mock.validate_update.return_value = None
    return mock

@pytest.fixture
def item_service(mock_geo_service, mock_event_emitter, mock_validator):
    """Create item service with mocked dependencies"""
    return ItemService(
        geo_service=mock_geo_service,
        event_emitter=mock_event_emitter,
        validator=mock_validator
    )

@pytest.fixture
def valid_item_data():
    """Valid item data for testing"""
    start_date = datetime.now(timezone.utc) + timedelta(days=10)
    return ItemCreate(
        name="Test Item",
        postcode="10001",
        title="Test Title",
        users=["Test Item", "Another User"],
        start_date=start_date
    )

@pytest.fixture
def valid_update_data():
    """Valid update data for testing"""
    return ItemUpdate(
        title="Updated Title"
    )

@pytest.mark.asyncio
async def test_get_all_items(item_service):
    """Test getting all items"""
    # Setup mock data
    Item.objects = MagicMock()
    Item.objects.all.return_value = [
        MagicMock(id="1", name="Item 1"),
        MagicMock(id="2", name="Item 2")
    ]

    # Call service
    result = await item_service.get_all_items()

    # Assert
    assert len(result) == 2
    Item.objects.all.assert_called_once()

@pytest.mark.asyncio
async def test_get_item_by_id_success(item_service):
    """Test getting an item by ID successfully"""
    # Setup mock data
    mock_item = MagicMock(id="1", name="Item 1")
    Item.objects = MagicMock()
    Item.objects.return_value.first.return_value = mock_item

    # Call service
    result = await item_service.get_item_by_id("1")

    # Assert
    assert result == mock_item
    Item.objects.assert_called_once_with(id="1")

@pytest.mark.asyncio
async def test_get_item_by_id_not_found(item_service):
    """Test getting a non-existent item by ID"""
    # Setup mock data
    Item.objects = MagicMock()
    Item.objects.return_value.first.return_value = None

    # Call service and assert
    with pytest.raises(NotFoundError):
        await item_service.get_item_by_id("999")

@pytest.mark.asyncio
async def test_create_item_success(item_service, valid_item_data, mock_geo_service, mock_event_emitter, mock_validator):
    """Test creating an item successfully"""
    # Setup mock data
    mock_item = MagicMock()
    mock_item.save.return_value = None
    mock_item.id = "test_id"

    # Mock Item class
    with patch('app.features.items.service.Item', return_value=mock_item) as mock_item_class:
        # Call service
        result = await item_service.create_item(valid_item_data)

        # Assert
        assert result == mock_item
        mock_validator.validate_create.assert_called_once_with(valid_item_data)
        mock_geo_service.get_location_data.assert_called_once_with(valid_item_data.postcode)
        mock_item.save.assert_called_once()
        mock_event_emitter.emit.assert_called_once_with("item.created", {"item_id": "test_id"})

@pytest.mark.asyncio
async def test_create_item_geo_error(item_service, valid_item_data, mock_geo_service, mock_event_emitter, mock_validator):
    """Test creating an item when geo service fails"""
    # Setup mock data
    mock_item = MagicMock()
    mock_item.save.return_value = None
    mock_item.id = "test_id"

    # Setup geo service to raise error
    mock_geo_service.get_location_data.side_effect = ExternalServiceError("Geo service error")

    # Mock Item class
    with patch('app.features.items.service.Item', return_value=mock_item) as mock_item_class:
        # Call service
        result = await item_service.create_item(valid_item_data)

        # Assert
        assert result == mock_item
        mock_validator.validate_create.assert_called_once_with(valid_item_data)
        mock_geo_service.get_location_data.assert_called_once_with(valid_item_data.postcode)
        mock_item.save.assert_called_once()
        mock_event_emitter.emit.assert_called_once_with("item.created", {"item_id": "test_id"})
        # Check that null geo data was set
        mock_item_class.assert_called_once()
        call_kwargs = mock_item_class.call_args.kwargs
        assert call_kwargs["latitude"] is None
        assert call_kwargs["longitude"] is None
        assert call_kwargs["direction_from_new_york"] is None

@pytest.mark.asyncio
async def test_update_item_success(item_service, valid_update_data, mock_event_emitter, mock_validator):
    """Test updating an item successfully"""
    # Setup mock data
    mock_item = MagicMock()
    mock_item.to_dict.return_value = {"id": "1", "name": "Item 1", "title": "Old Title"}
    mock_item.save.return_value = None
    mock_item.id = "test_id"

    # Mock get_item_by_id
    with patch.object(item_service, 'get_item_by_id', return_value=mock_item) as mock_get_item:
        # Call service
        result = await item_service.update_item("1", valid_update_data)

        # Assert
        assert result == mock_item
        mock_get_item.assert_called_once_with("1")
        mock_validator.validate_update.assert_called_once()
        mock_item.save.assert_called_once()
        mock_event_emitter.emit.assert_called_once_with("item.updated", {"item_id": "test_id"})
        # Check that title was updated
        assert mock_item.title == valid_update_data.title

@pytest.mark.asyncio
async def test_delete_item_success(item_service, mock_event_emitter):
    """Test deleting an item successfully"""
    # Setup mock data
    mock_item = MagicMock(id="test_id")
    mock_item.delete.return_value = None

    # Mock get_item_by_id
    with patch.object(item_service, 'get_item_by_id', return_value=mock_item) as mock_get_item:
        # Call service
        result = await item_service.delete_item("test_id")

        # Assert
        assert result is True
        mock_get_item.assert_called_once_with("test_id")
        mock_item.delete.assert_called_once()
        mock_event_emitter.emit.assert_called_once_with("item.deleted", {"item_id": "test_id"})