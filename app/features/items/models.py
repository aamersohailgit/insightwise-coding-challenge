import datetime
from mongoengine import Document, StringField, FloatField, ListField, DateTimeField, BooleanField
from enum import Enum

class Direction(str, Enum):
    NE = "NE"
    NW = "NW"
    SE = "SE"
    SW = "SW"

class Item(Document):
    name = StringField(required=True, max_length=50)
    postcode = StringField(required=True)
    latitude = FloatField()
    longitude = FloatField()
    direction_from_new_york = StringField(choices=[d.value for d in Direction])
    title = StringField(required=False)
    users = ListField(StringField(max_length=50))
    start_date = DateTimeField(required=True)
    created_at = DateTimeField(default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = DateTimeField(default=datetime.datetime.now(datetime.timezone.utc))

    meta = {
        'collection': 'items',
        'indexes': [
            'name',
            'postcode',
            'created_at'
        ]
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now(datetime.timezone.utc)
        return super(Item, self).save(*args, **kwargs)

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'postcode': self.postcode,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'direction_from_new_york': self.direction_from_new_york,
            'title': self.title,
            'users': self.users,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
