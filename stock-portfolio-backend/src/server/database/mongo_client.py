import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

print(os.environ)
print("Initializing Mongo Client", os.getenv("MONGO_URI"))
mongo_client = MongoClient(os.getenv("MONGO_URI"))


def init_mongo_client(uri: str) -> MongoClient:
    global mongo_client
    if mongo_client is None:
        mongo_client = MongoClient(uri)
    return mongo_client


def get_mongo_client() -> MongoClient:
    return mongo_client


def close_mongo_client():
    global mongo_client
    mongo_client.close()
