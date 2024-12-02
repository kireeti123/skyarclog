"""
MongoDB listener for advanced logging framework.
"""

import json
try:
    import pymongo
except ImportError:
    print("MongoDB listener requires pymongo package")

from .base import BaseListener

class MongoDBListener(BaseListener):
    """
    Listener that logs to MongoDB
    """
    def __init__(self, host: str, port: int, database: str, collection: str):
        """
        Initialize MongoDB listener
        
        :param host: MongoDB server host
        :param port: MongoDB server port
        :param database: Database name
        :param collection: Collection name for logs
        """
        self.client = pymongo.MongoClient(host, port)
        self.db = self.client[database]
        self.collection = self.db[collection]

    def emit(self, log_entry: str):
        """
        Insert log entry into MongoDB
        
        :param log_entry: Formatted log entry
        """
        try:
            log_data = json.loads(log_entry)
            self.collection.insert_one(log_data)
        except Exception as e:
            print(f"MongoDB logging error: {e}")
