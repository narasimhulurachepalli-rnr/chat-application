import pymongo
import sys

try:
    from config import MONGO_URI, DB_NAME
except ImportError:
    from .config import MONGO_URI, DB_NAME

# Lazily initialize MongoClient so PyMongo handles connections/reconnections on demand
client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client[DB_NAME]
users_collection = db["users"]
chats_collection = db["chats"]
print("Database collections initialized lazily.")

