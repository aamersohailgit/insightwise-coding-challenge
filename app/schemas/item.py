from datetime import datetime, timedelta, timezone
from typing import List, Optional, Literal

from pydantic import BaseModel, Field, validator

class ItemBase(BaseModel):
    """Base schema for Item."""
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ItemCreate(ItemBase):
    """Schema for creating a new Item."""
    name: str = Field(..., min_length=1, max_length=50)
    postcode: str
    title: Optional[str] = None
    users: List[str] = Field(default_factory=list)
    startDate: datetime

    @validator('postcode')
    def validate_postcode(cls, v):
        """Validate postcode format."""
        import re
        if not re.match(r'^\d{5}(-\d{4})?$', v):
            raise ValueError('Invalid US postcode format')
        return v

    @validator('startDate')
    def validate_start_date(cls, v):
        """Validate start date is at least 1 week from now."""
        min_date = datetime.utcnow() + timedelta(days=7)
        if v.tzinfo is not None:
            min_date = min_date.replace(tzinfo=timezone.utc)
        if v < min_date:
            raise ValueError('Start date must be at least 1 week after creation')
        return v

    @validator('users')
    def validate_name_in_users(cls, v, values):
        """Validate that name is in users list."""
        if 'name' in values and values['name'] not in v:
            return v + [values['name']]
        return v

class ItemUpdate(ItemBase):
    """Schema for updating an Item."""
    name: Optional[str] = None
    title: Optional[str] = None
    users: Optional[List[str]] = None
    startDate: Optional[datetime] = None

    @validator('startDate')
    def validate_start_date(cls, v):
        """Validate start date is at least 1 week from now."""
        if v is not None:
            min_date = datetime.utcnow() + timedelta(days=7)
            if v.tzinfo is not None:
                min_date = min_date.replace(tzinfo=timezone.utc)
            if v < min_date:
                raise ValueError('Start date must be at least 1 week after creation')
        return v

class ItemResponse(ItemBase):
    """Schema for Item response."""
    id: str
    name: str
    postcode: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    directionFromNewYork: Optional[Literal["NE", "NW", "SE", "SW"]] = None
    title: Optional[str] = None
    users: List[str]
    startDate: datetime
    createdAt: datetime
    updatedAt: datetime