import os
import pytest
from fastapi.testclient import TestClient
import mongomock
import mongoengine

from app.main import app
from app.config import config

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Set up test database with MongoMock."""
    # Use MongoMock directly since the mongo_client_class option is not working
    mongodb_client = mongomock.MongoClient()
    db = mongodb_client[config.MONGODB_DB]

    # Patch mongoengine's default connection
    mongoengine.connection._connections = {}
    mongoengine.connection._connection_settings = {}
    mongoengine.connection._dbs = {}

    # Register the default connection
    mongoengine.connection.register_connection(
        alias="default",
        name=config.MONGODB_DB,
        host="mongomock://localhost"
    )

    yield

    # Clean up
    mongoengine.connection.disconnect()

@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def auth_headers():
    """
    Authentication headers fixture
    """
    return {"Authorization": "Bearer test-token"}