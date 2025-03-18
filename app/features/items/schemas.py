from typing import Optional, List
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, Field, validator
import re

class ItemBase(BaseModel):
    name: str = Field(..., max_length=50)
    postcode: str
    title: Optional[str] = None
    users: List[str] = Field(default_factory=list)

    @validator('postcode')
    def validate_postcode(cls, v):
        # US postal code pattern: 5 digits or 5+4 format (ZIP+4)
        pattern = r'^\d{5}(?:-\d{4})?$'
        if not re.match(pattern, v):
            raise ValueError('Must be a valid US postcode (5 digits or ZIP+4 format)')
        return v

    @validator('users')
    def validate_users(cls, v):
        for name in v:
            if len(name) >= 50:
                raise ValueError(f'User name "{name}" must be less than 50 characters')
        return v

class ItemCreate(ItemBase):
    start_date: datetime

    @validator('start_date')
    def validate_start_date(cls, v):
        # Get current time in UTC
        now = datetime.now(timezone.utc)

        # Add 7 days to now
        min_date = now + timedelta(days=7)

        # Ensure v is timezone aware for comparison
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)

        if v < min_date:
            raise ValueError('Start date must be at least 1 week after the item creation date')
        return v

class ItemUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=50)
    title: Optional[str] = None
    users: Optional[List[str]] = None
    start_date: Optional[datetime] = None

    @validator('users')
    def validate_users(cls, v):
        if v is not None:
            for name in v:
                if len(name) >= 50:
                    raise ValueError(f'User name "{name}" must be less than 50 characters')
        return v

    @validator('start_date')
    def validate_start_date(cls, v):
        if v:
            # Get current time in UTC
            now = datetime.now(timezone.utc)

            # Add 7 days to now
            min_date = now + timedelta(days=7)

            # Ensure v is timezone aware for comparison
            if v.tzinfo is None:
                v = v.replace(tzinfo=timezone.utc)

            if v < min_date:
                raise ValueError('Start date must be at least 1 week after the current date')
        return v

class ItemInDB(ItemBase):
    id: str
    latitude: float
    longitude: float
    direction_from_new_york: str
    start_date: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ItemResponse(ItemInDB):
    pass
