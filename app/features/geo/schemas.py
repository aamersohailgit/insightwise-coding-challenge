from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class GeoData(BaseModel):
    latitude: float
    longitude: float

class GeoCacheBase(BaseModel):
    postcode: str
    latitude: float
    longitude: float

class GeoCacheCreate(GeoCacheBase):
    pass

class GeoCacheInDB(GeoCacheBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class GeoCacheResponse(GeoCacheInDB):
    pass

class PostcodeRequest(BaseModel):
    postcode: str = Field(..., description="US postcode to get location data for")
