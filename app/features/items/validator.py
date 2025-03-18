from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from app.features.items.schemas import ItemCreate, ItemUpdate
from app.utils.errors import ValidationError

class ItemValidatorInterface(ABC):
    """Interface for item validators"""

    @abstractmethod
    def validate_create(self, data: ItemCreate) -> None:
        """Validate item creation data"""
        pass

    @abstractmethod
    def validate_update(self, data: ItemUpdate, existing_item: Any = None) -> None:
        """Validate item update data"""
        pass

class DefaultItemValidator(ItemValidatorInterface):
    """Default implementation of item validator"""

    def validate_create(self, data: ItemCreate) -> None:
        """
        Validate item creation data

        Args:
            data: ItemCreate data to validate

        Raises:
            ValidationError: If validation fails
        """
        # Check required fields
        if not data.name:
            raise ValidationError("Item name cannot be empty")

        if not data.postcode:
            raise ValidationError("Item postcode cannot be empty")

        if not data.title:
            raise ValidationError("Item title cannot be empty")

        if not data.users or len(data.users) == 0:
            raise ValidationError("At least one user must be specified")

        # Validate start date is in the future
        if data.start_date and data.start_date <= datetime.now(timezone.utc):
            raise ValidationError("Item start date must be in the future")

    def validate_update(self, data: ItemUpdate, existing_item: Any = None) -> None:
        """
        Validate item update data

        Args:
            data: ItemUpdate data to validate
            existing_item: The existing item to be updated

        Raises:
            ValidationError: If validation fails
        """
        # Convert to dict for easier processing if needed
        item_dict = {}
        if existing_item:
            try:
                item_dict = existing_item.to_dict()
            except (AttributeError, TypeError):
                # If to_dict doesn't exist or fails, try using __dict__
                try:
                    item_dict = existing_item.__dict__
                except AttributeError:
                    # If both fail, just continue with validation without existing item data
                    pass

        # Check if any fields were provided for update
        if data.dict(exclude_unset=True, exclude_defaults=True, exclude_none=True) == {}:
            raise ValidationError("No fields provided for update")

        # Validate fields that are being updated
        if hasattr(data, 'name') and data.name is not None and not data.name:
            raise ValidationError("Item name cannot be empty")

        if hasattr(data, 'title') and data.title is not None and not data.title:
            raise ValidationError("Item title cannot be empty")

        if hasattr(data, 'postcode') and data.postcode is not None and not data.postcode:
            raise ValidationError("Item postcode cannot be empty")

        if hasattr(data, 'users') and data.users is not None and len(data.users) == 0:
            raise ValidationError("At least one user must be specified")

        # Validate start date is in the future if being updated
        if hasattr(data, 'start_date') and data.start_date is not None:
            if data.start_date <= datetime.now(timezone.utc):
                raise ValidationError("Item start date must be in the future")