import os
import pytest
import mongoengine
from mongomock import MongoClient
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="function", autouse=True)
def setup_db():
    """
    Set up the database connection for tests.
    This fixture runs automatically for every test.
    """
    mongoengine.disconnect_all()
    mongoengine.connect('testdb', host='mongodb://localhost', mongo_client_class=MongoClient)

    yield

    mongoengine.disconnect_all()


@pytest.fixture
def client():
    """
    FastAPI test client fixture
    """
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """
    Authentication headers fixture
    """
    return {"Authorization": "Bearer test-token"}