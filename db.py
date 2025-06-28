from pymongo import AsyncMongoClient
import os

# Init: the MongoDB client with the URI from .env variables
# The .env file contains default MONGO_URI="mongodb://localhost:27017"
# Replace variable with your own mongodb uri
mongo_client = AsyncMongoClient(os.environ.get("MONGO_URI"))