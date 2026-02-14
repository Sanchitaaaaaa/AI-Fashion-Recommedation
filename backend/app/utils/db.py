from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")

# Connect to MongoDB
try:
    client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    db = client["ai_fashion"]
    print("✅ Connected to MongoDB")
except Exception as e:
    print(f"❌ Error connecting to MongoDB: {str(e)}")
    raise

# Define collections
users_collection = db["users"]
user_images_collection = db["user_images"]
user_features_collection = db["user_features"]
outfits_collection = db["outfits"]

# Create indexes
try:
    users_collection.create_index("user_id", unique=True)
    user_images_collection.create_index("user_id")
    user_images_collection.create_index("image_id", unique=True)
    user_features_collection.create_index("image_id", unique=True)
    user_features_collection.create_index("user_id")
    outfits_collection.create_index("outfit_name", unique=True)
    print("✅ Database indexes created")
except Exception as e:
    print(f"⚠️  Warning creating indexes: {str(e)}")

__all__ = ['client', 'db', 'users_collection', 'user_images_collection', 'user_features_collection', 'outfits_collection']