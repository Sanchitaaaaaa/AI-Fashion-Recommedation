"""Outfit Processor Service"""
from app.utils.db import db
from typing import List, Dict, Any

def get_outfits_count() -> int:
    """Get count of outfits in database"""
    try:
        outfits_collection = db["outfits"]
        count = outfits_collection.count_documents({})
        print(f"✅ Outfit count: {count}")
        return count
    except Exception as e:
        print(f"❌ Error getting outfit count: {str(e)}")
        return 0

def get_all_outfits() -> List[Dict[str, Any]]:
    """Get all outfits from database"""
    try:
        outfits_collection = db["outfits"]
        outfits = list(outfits_collection.find({}, {"_id": 0}))
        print(f"✅ Retrieved {len(outfits)} outfits")
        return outfits
    except Exception as e:
        print(f"❌ Error getting outfits: {str(e)}")
        return []

def get_outfit_by_name(name: str) -> Dict[str, Any]:
    """Get specific outfit by name"""
    try:
        outfits_collection = db["outfits"]
        outfit = outfits_collection.find_one({"name": name}, {"_id": 0})
        if outfit:
            print(f"✅ Found outfit: {name}")
        return outfit
    except Exception as e:
        print(f"❌ Error getting outfit: {str(e)}")
        return None