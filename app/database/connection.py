from pymongo import MongoClient
from app.core.config import settings

class DatabaseManager:
    client: MongoClient = None

    def connect(self):
        self.client = MongoClient(settings.MONGO_URI)
        print("Connected to MongoDB")

    def get_database(self):
        return self.client[settings.DB_NAME]
    
    def get_client(self):
        return self.client

    def close(self):
        if self.client:
            self.client.close()

db_manager = DatabaseManager()