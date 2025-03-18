import datetime
from mongoengine import Document, StringField, BooleanField, DateTimeField, ListField

class User(Document):
    username = StringField(required=True, unique=True)
    email = StringField(required=True, unique=True)
    hashed_password = StringField(required=True)
    is_active = BooleanField(default=True)
    is_superuser = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    updated_at = DateTimeField(default=datetime.datetime.utcnow)

    meta = {
        'collection': 'users',
        'indexes': [
            'username',
            'email'
        ]
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.utcnow()
        return super(User, self).save(*args, **kwargs)
