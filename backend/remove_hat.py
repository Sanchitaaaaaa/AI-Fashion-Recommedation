#!/usr/bin/env python3
"""
Remove hat and shoes from MongoDB outfits collection
"""

from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")

if not MONGO_URL:
    print("❌ MONGO_URL not set in .env")
    exit(1)

try:
    client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=10000)
    db = client["ai_fashion"]
    collection = db["outfits"]
    print("✅ Connected to MongoDB\n")
    
    # Count before
    total_before = collection.count_documents({})
    hat_count = collection.count_documents({"category": "hat"})
    shoes_count = collection.count_documents({"category": "shoes"})
    
    print(f"Before deletion:")
    print(f"  Total outfits: {total_before}")
    print(f"  Hat outfits: {hat_count}")
    print(f"  Shoes outfits: {shoes_count}\n")
    
    # Delete hat
    result_hat = collection.delete_many({"category": "hat"})
    print(f"✅ Deleted {result_hat.deleted_count} hat outfits")
    
    # Delete shoes
    result_shoes = collection.delete_many({"category": "shoes"})
    print(f"✅ Deleted {result_shoes.deleted_count} shoes outfits\n")
    
    # Count after
    total_after = collection.count_documents({})
    print(f"After deletion:")
    print(f"  Total outfits: {total_after}")
    print(f"  Remaining categories:")
    
    categories = collection.aggregate([
        {"$group": {"_id": "$category", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ])
    
    for cat in categories:
        print(f"    - {cat['_id']}: {cat['count']}")
    
    print(f"\n✅ SUCCESS!")
    print(f"Removed {hat_count + shoes_count} items")
    print(f"Remaining: {total_after} items")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    exit(1)