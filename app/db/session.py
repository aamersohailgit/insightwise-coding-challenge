from mongoengine import connect, disconnect
from app.config import config

def get_db():
    return connect(
        db=config.MONGODB_DB,
        host=config.MONGODB_URL
    )

def close_db():
    disconnect()
