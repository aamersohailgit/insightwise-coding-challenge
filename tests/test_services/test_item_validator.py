import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock
from pydantic import ValidationError as PydanticValidationError

from app.features.items.schemas import ItemCreate, ItemUpdate
from app.features.items.validator import ItemValidatorInterface, DefaultItemValidator
from app.utils.errors import ValidationError

@pytest.fixture
def item_validator():
    """Create item validator for testing"""
    return DefaultItemValidator()

@pytest.fixture
def future_date():
    """Create a date 10 days in the future for testing"""
    return datetime.now(timezone.utc) + timedelta(days=10)

@pytest.fixture
def past_date():
    """Create a date 3 days in the future - not far enough in the future for validation"""
    return datetime.now(timezone.utc) + timedelta(days=3)

class TestDefaultItemValidator:
    """Test suite for DefaultItemValidator"""

    def test_validate_create_valid_data(self, item_validator, future_date):
        """Test validation with valid create data"""
        # Create valid item data
        data = ItemCreate(
            name="Test Item",
            postcode="10001",
            title="Test Title",
            users=["User 1", "User 2"],
            start_date=future_date
        )

        # Validation should succeed (no exception raised)
        item_validator.validate_create(data)

    def test_validate_create_empty_name(self, item_validator, future_date):
        """Test validation fails with empty name"""
        # Create valid item data first
        data = ItemCreate(
            name="Test Item",
            postcode="10001",
            title="Test Title",
            users=["User 1", "User 2"],
            start_date=future_date
        )

        # Then manually set name to empty to bypass pydantic validation
        data.name = ""

        # Validation should fail
        with pytest.raises(ValidationError) as exc_info:
            item_validator.validate_create(data)

        assert "name cannot be empty" in str(exc_info.value).lower()

    def test_validate_create_empty_title(self, item_validator, future_date):
        """Test validation fails with empty title"""
        # Create valid item data first
        data = ItemCreate(
            name="Test Item",
            postcode="10001",
            title="Test Title",
            users=["User 1", "User 2"],
            start_date=future_date
        )

        # Then manually set title to empty to bypass pydantic validation
        data.title = ""

        # Validation should fail
        with pytest.raises(ValidationError) as exc_info:
            item_validator.validate_create(data)

        assert "title cannot be empty" in str(exc_info.value).lower()

    def test_validate_create_empty_users(self, item_validator, future_date):
        """Test validation fails with empty users list"""
        # Create valid item data first
        data = ItemCreate(
            name="Test Item",
            postcode="10001",
            title="Test Title",
            users=["User 1", "User 2"],
            start_date=future_date
        )

        # Then manually set users to empty list to bypass pydantic validation
        data.users = []

        # Validation should fail
        with pytest.raises(ValidationError) as exc_info:
            item_validator.validate_create(data)

        assert "user must be specified" in str(exc_info.value).lower()

    def test_validate_create_past_date(self, item_validator, future_date):
        """Test validation fails with near future start date"""
        # Create valid item data first
        data = ItemCreate(
            name="Test Item",
            postcode="10001",
            title="Test Title",
            users=["User 1", "User 2"],
            start_date=future_date
        )

        # Then manually set date to past to bypass pydantic validation
        data.start_date = datetime.now(timezone.utc) - timedelta(days=1)

        # Validation should fail
        with pytest.raises(ValidationError) as exc_info:
            item_validator.validate_create(data)

        assert "start date must be in the future" in str(exc_info.value).lower()

    def test_validate_update_valid_data(self, item_validator):
        """Test validation with valid update data"""
        # Create valid update data
        data = ItemUpdate(title="Updated Title")

        # Create mock item to update
        mock_item = MagicMock()
        mock_item.to_dict.return_value = {
            "name": "Test Item",
            "postcode": "10001",
            "title": "Original Title",
            "users": ["User 1", "User 2"],
            "start_date": datetime.now(timezone.utc) + timedelta(days=10)
        }

        # Validation should succeed (no exception raised)
        item_validator.validate_update(data, mock_item)

    def test_validate_update_empty_title(self, item_validator):
        """Test validation fails with empty title update"""
        # Create valid update data first
        data = ItemUpdate(title="Valid Title")

        # Then manually set title to empty to bypass pydantic validation
        data.title = ""

        # Create mock item to update
        mock_item = MagicMock()
        mock_item.to_dict.return_value = {
            "name": "Test Item",
            "postcode": "10001",
            "title": "Original Title",
            "users": ["User 1", "User 2"],
            "start_date": datetime.now(timezone.utc) + timedelta(days=10)
        }

        # Validation should fail
        with pytest.raises(ValidationError) as exc_info:
            item_validator.validate_update(data, mock_item)

        assert "title cannot be empty" in str(exc_info.value).lower()

    def test_validate_update_empty_users(self, item_validator):
        """Test validation fails with empty users update"""
        # Create valid update data first - empty users would normally be caught by pydantic
        data = ItemUpdate(users=["User 1"])

        # Then manually set users to empty to bypass pydantic validation
        data.users = []

        # Create mock item to update
        mock_item = MagicMock()
        mock_item.to_dict.return_value = {
            "name": "Test Item",
            "postcode": "10001",
            "title": "Original Title",
            "users": ["User 1", "User 2"],
            "start_date": datetime.now(timezone.utc) + timedelta(days=10)
        }

        # Validation should fail
        with pytest.raises(ValidationError) as exc_info:
            item_validator.validate_update(data, mock_item)

        assert "user must be specified" in str(exc_info.value).lower()

    def test_validate_update_past_date(self, item_validator):
        """Test validation fails with past start date update"""
        # Create valid update data first
        data = ItemUpdate(start_date=datetime.now(timezone.utc) + timedelta(days=10))

        # Then manually set start_date to past to bypass pydantic validation
        data.start_date = datetime.now(timezone.utc) - timedelta(days=1)

        # Create mock item to update
        mock_item = MagicMock()
        mock_item.to_dict.return_value = {
            "name": "Test Item",
            "postcode": "10001",
            "title": "Original Title",
            "users": ["User 1", "User 2"],
            "start_date": datetime.now(timezone.utc) + timedelta(days=10)
        }

        # Validation should fail
        with pytest.raises(ValidationError) as exc_info:
            item_validator.validate_update(data, mock_item)

        assert "start date must be in the future" in str(exc_info.value).lower()