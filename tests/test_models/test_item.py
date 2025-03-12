import pytest
from datetime import datetime, timedelta

from app.models.item import Item


def test_item_valid():
    start_date = datetime.utcnow() + timedelta(days=10)
    item = Item(
        name="Test Item",
        postcode="12345",
        title="Test Title",
        users=["Test Item", "User 1"],
        start_date=start_date
    )
    item.clean()


def test_item_invalid_postcode():
    with pytest.raises(Exception):
        start_date = datetime.utcnow() + timedelta(days=10)
        item = Item(
            name="Test Item",
            postcode="invalid",
            title="Test Title",
            users=["Test Item", "User 1"],
            start_date=start_date
        )
        item.clean()


def test_item_invalid_start_date():
    with pytest.raises(Exception):
        start_date = datetime.utcnow() + timedelta(days=2)  # Less than a week
        item = Item(
            name="Test Item",
            postcode="12345",
            title="Test Title",
            users=["Test Item", "User 1"],
            start_date=start_date
        )
        item.clean()