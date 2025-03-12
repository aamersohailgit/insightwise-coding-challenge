import os
import pytest
from unittest.mock import patch, MagicMock
import mongoengine

from app.db.mongo import init_db, close_db


def test_init_db_with_mock():
    """Test initializing the database with mock connection."""
    # Ensure USE_MOCK_DB is set to true
    with patch.dict(os.environ, {"USE_MOCK_DB": "true"}):
        # Mock mongoengine.connect to verify it's called correctly
        with patch('mongoengine.connect') as mock_connect:
            init_db()

            # Verify connect was called with expected parameters
            mock_connect.assert_called_once()
            # Verify MongoClient was used in the call
            args, kwargs = mock_connect.call_args
            assert kwargs['mongo_client_class'].__name__ == 'MongoClient'


def test_init_db_with_real_connection():
    """Test initializing the database with a real connection."""
    # Set USE_MOCK_DB to false and patch environment variables
    with patch.dict(os.environ, {"USE_MOCK_DB": "false"}):
        # Mock the environment variables directly in the module
        with patch('app.db.mongo.MONGODB_URL', 'mongodb://testhost:27017/'), \
             patch('app.db.mongo.MONGODB_DB', 'test_db'), \
             patch('mongoengine.connect') as mock_connect:

            init_db()

            # Verify connect was called with expected parameters
            # Note: The actual implementation includes mongo_client_class even when USE_MOCK_DB is false
            mock_connect.assert_called_once()
            args, kwargs = mock_connect.call_args
            assert kwargs['host'] == 'mongodb://testhost:27017/'
            assert args[0] == 'test_db'


def test_init_db_connection_error():
    """Test handling of connection errors."""
    # Mock mongoengine.connect to raise an exception
    with patch('mongoengine.connect', side_effect=Exception("Connection error")):
        # Verify the error is re-raised
        with pytest.raises(Exception, match="Connection error"):
            init_db()


def test_close_db():
    """Test closing the database connection."""
    # Mock mongoengine.disconnect to verify it's called
    with patch('mongoengine.disconnect') as mock_disconnect:
        close_db()

        # Verify disconnect was called
        mock_disconnect.assert_called_once()