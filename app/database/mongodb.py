"""
MongoDB Database Connection
Using Motor async driver
"""

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings


class MongoDB:
    """MongoDB connection manager"""
    
    def __init__(self):
        self.client: AsyncIOMotorClient = None
        self.database = None
    
    def connect(self):
        """Connect to MongoDB"""
        self.client = AsyncIOMotorClient(settings.MONGODB_URL)
        self.database = self.client[settings.MONGODB_DATABASE]
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
    
    def get_collection(self, name: str):
        """Get a collection"""
        return self.database[name]


# Global MongoDB instance
mongodb = MongoDB()
mongodb.connect()


# Dependency for getting MongoDB
async def get_mongodb():
    """Get MongoDB database"""
    return mongodb.database
