import os
import logging

import mongoengine
from mongomock import MongoClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
MONGODB_DB = os.getenv("MONGODB_DB", "items_db")
USE_MOCK_DB = os.getenv("USE_MOCK_DB", "true").lower() == "true"

def init_db():
    """Initialize database connection."""
    try:
        if USE_MOCK_DB:
            logger.info("Setting up MongoMock connection")
            mongoengine.connect(
                MONGODB_DB,
                host=MONGODB_URL,
                mongo_client_class=MongoClient
            )
        else:
            logger.info(f"Connecting to MongoDB at {MONGODB_URL}")
            mongoengine.connect(
                MONGODB_DB,
                host=MONGODB_URL
            )

        logger.info(f"Connected to MongoDB (db: {MONGODB_DB})")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        raise

def close_db():
    """Close database connection."""
    mongoengine.disconnect()
    logger.info("Disconnected from MongoDB")