from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from app.utils.db import db

router = APIRouter()

class WishlistItem(BaseModel):
    user_id: str
    outfit_name: str
    similarity_score: float = 0.0
    image_id: str = None

class RemoveWishlistItem(BaseModel):
    user_id: str
    outfit_name: str

class ClearWishlist(BaseModel):
    user_id: str

@router.post("/add")
async def add_to_wishlist(item: WishlistItem):
    """Add outfit to user's wishlist"""
    try:
        wishlist_collection = db["wishlist"]
        
        # Check if already in wishlist
        existing = wishlist_collection.find_one({
            "user_id": item.user_id,
            "outfit_name": item.outfit_name
        })
        
        if existing:
            return {
                "success": True,
                "message": "Already in wishlist"
            }
        
        # Add to wishlist
        wishlist_item = {
            "user_id": item.user_id,
            "outfit_name": item.outfit_name,
            "similarity_score": item.similarity_score,
            "image_id": item.image_id,
            "saved_date": datetime.utcnow()
        }
        
        result = wishlist_collection.insert_one(wishlist_item)
        
        return {
            "success": True,
            "message": "Added to wishlist",
            "item_id": str(result.inserted_id)
        }
    
    except Exception as e:
        print(f"Error adding to wishlist: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error adding to wishlist: {str(e)}")

@router.post("/remove")
async def remove_from_wishlist(item: RemoveWishlistItem):
    """Remove outfit from user's wishlist"""
    try:
        wishlist_collection = db["wishlist"]
        
        result = wishlist_collection.delete_one({
            "user_id": item.user_id,
            "outfit_name": item.outfit_name
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Item not found in wishlist")
        
        return {
            "success": True,
            "message": "Removed from wishlist"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error removing from wishlist: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error removing from wishlist: {str(e)}")

@router.post("/clear")
async def clear_wishlist(data: ClearWishlist):
    """Clear entire wishlist for user"""
    try:
        wishlist_collection = db["wishlist"]
        
        result = wishlist_collection.delete_many({
            "user_id": data.user_id
        })
        
        return {
            "success": True,
            "message": f"Cleared {result.deleted_count} items from wishlist",
            "deleted_count": result.deleted_count
        }
    
    except Exception as e:
        print(f"Error clearing wishlist: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error clearing wishlist: {str(e)}")

@router.get("/get")
async def get_wishlist(user_id: str):
    """Get all wishlist items for user"""
    try:
        wishlist_collection = db["wishlist"]
        
        items = list(wishlist_collection.find(
            {"user_id": user_id},
            {"_id": 0}
        ).sort("saved_date", -1))
        
        return {
            "success": True,
            "user_id": user_id,
            "items": items,
            "total": len(items)
        }
    
    except Exception as e:
        print(f"Error fetching wishlist: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching wishlist: {str(e)}")

@router.get("/count")
async def get_wishlist_count(user_id: str):
    """Get wishlist count for user"""
    try:
        wishlist_collection = db["wishlist"]
        
        count = wishlist_collection.count_documents({"user_id": user_id})
        
        return {
            "success": True,
            "user_id": user_id,
            "count": count
        }
    
    except Exception as e:
        print(f"Error getting wishlist count: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")