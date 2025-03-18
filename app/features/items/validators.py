from typing import Dict, Any, Protocol, runtime_checkable
from app.features.items.schemas import ItemCreate, ItemUpdate
from app.utils.errors import ValidationError

@runtime_checkable
class ItemValidator(Protocol):
    """Interface for item validators"""
    def validate_create(self, data: ItemCreate) -> None: ...
    def validate_update(self, item_data: Dict[str, Any], update_data: Dict[str, Any]) -> None: ...

class DefaultItemValidator:
    """Default implementation of item validator"""

    def validate_create(self, data: ItemCreate) -> None:
        """Validate item data for creation"""
        if data.name not in data.users:
            raise ValidationError(
                message="The name field must be included in the users list",
                details={"name": data.name, "users": data.users}
            )

    def validate_update(self, item_data: Dict[str, Any], update_data: Dict[str, Any]) -> None:
        """Validate item data for update"""
        # Validate that name is in users list if both are being updated
        if "name" in update_data and "users" in update_data:
            if update_data["name"] not in update_data["users"]:
                raise ValidationError(
                    message="The name field must be included in the users list",
                    details={"name": update_data["name"], "users": update_data["users"]}
                )
        # Validate if only users is being updated but name already exists
        elif "users" in update_data and item_data.get("name") not in update_data["users"]:
            raise ValidationError(
                message="The name field must be included in the users list",
                details={"name": item_data.get("name"), "users": update_data["users"]}
            )

# Default validator instance
item_validator = DefaultItemValidator()