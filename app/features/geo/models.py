from mongoengine import Document, StringField, FloatField, DateTimeField
import datetime

class GeoCache(Document):
    postcode = StringField(required=True, unique=True)
    latitude = FloatField(required=True)
    longitude = FloatField(required=True)
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    updated_at = DateTimeField(default=datetime.datetime.utcnow)

    meta = {
        'collection': 'geo_cache',
        'indexes': [
            'postcode',
            'created_at'
        ]
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.utcnow()
        return super(GeoCache, self).save(*args, **kwargs)
