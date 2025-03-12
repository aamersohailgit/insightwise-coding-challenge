import os
import pytest
import mongoengine
from mongomock import MongoClient
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="function")
def client():
    """
    Test client fixture with mocked database
    """
    mongoengine.disconnect_all()
    mongoengine.connect('testdb', host='mongodb://localhost', mongo_client_class=MongoClient)

    test_client = TestClient(app)

    yield test_client

    mongoengine.disconnect_all()


@pytest.fixture
def auth_headers():
    """
    Authentication headers fixture
    """
    return {"Authorization": "Bearer test-token"}