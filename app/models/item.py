from datetime import datetime, timedelta
import re

import mongoengine as me

class Item(me.Document):
    """Item document model with all required fields."""
    # Required fields
    name = me.StringField(required=True, max_length=50)
    postcode = me.StringField(required=True)

    # Read-only fields, updated automatically
    latitude = me.FloatField()
    longitude = me.FloatField()
    direction_from_new_york = me.StringField(choices=["NE", "NW", "SE", "SW"])

    # Optional fields
    title = me.StringField(required=False)
    users = me.ListField(me.StringField(max_length=50))
    start_date = me.DateTimeField(required=True)

    # Metadata
    created_at = me.DateTimeField(default=datetime.utcnow)
    updated_at = me.DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'items',
        'indexes': ['name', 'postcode']
    }

    def clean(self):
        """Validate item fields before saving. postcode format (US postcode)"""
        if not re.match(r'^\d{5}(-\d{4})?$', self.postcode):
            raise me.ValidationError("Invalid US postcode format")

        # Validate start_date is at least 1 week after creation
        min_start_date = datetime.utcnow() + timedelta(days=7)
        if self.start_date and self.start_date < min_start_date:
            raise me.ValidationError("StartDate must be at least 1 week after creation date")

        # Update timestamps
        if not self.id:
            self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        """Convert document to dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "postcode": self.postcode,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "direction_from_new_york": self.direction_from_new_york,
            "title": self.title,
            "users": self.users,
            "start_date": self.start_date,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }