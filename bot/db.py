import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")

if not MONGODB_URI:
    raise ValueError("MONGODB_URI environment variable is required")

client = MongoClient(MONGODB_URI)
db = client.get_default_database()

def get_collection(name):
    return db[name]

def close_connection():
    client.close()
