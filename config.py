# config.py
from pymongo import MongoClient

# Replace the URI with your actual MongoDB URI
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "sensitive_content_db"
COLLECTION_NAME = "sensitive_vectors"

def get_database():
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]
