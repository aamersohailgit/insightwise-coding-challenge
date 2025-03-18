import os
import pytest
from fastapi.testclient import TestClient
from mongoengine import connect, disconnect
import mongomock

from app.main import app
from app.config import config

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Set up test database with MongoMock."""
    # Connect to a mock MongoDB
    conn = connect(
        db=config.MONGODB_DB,
        host='mongodb://localhost',
        mongo_client_class=mongomock.MongoClient
    )

    yield

    # Disconnect when done
    disconnect()

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