import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_V1_PREFIX = "/api/v1"
    PROJECT_NAME = "Items API"

    # Database settings
    MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
    MONGODB_DB = os.getenv("MONGODB_DB", "items_db")
    USE_MOCK_DB = os.getenv("USE_MOCK_DB", "true").lower() == "true"

    # External API
    ZIPOPOTAM_API_URL = "https://api.zippopotam.us/us/{postcode}"
    NEW_YORK_POSTCODE = "10001"
    NEW_YORK_LAT = 40.7506
    NEW_YORK_LON = -73.9971

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/items_api.log")
    LOG_ERROR_FILE = os.getenv("LOG_ERROR_FILE", "logs/items_api_errors.log")

    # Event system
    EVENT_MAX_WORKERS = int(os.getenv("EVENT_MAX_WORKERS", "5"))

config = Config()
