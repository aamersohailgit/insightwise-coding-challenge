from datetime import datetime
import mongoengine as me

class Item(me.Document):
    """Simple Item model."""
    name = me.StringField(required=True, max_length=50)
    created_at = me.DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'items'
    }