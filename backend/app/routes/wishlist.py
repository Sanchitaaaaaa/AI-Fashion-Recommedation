from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from bson import ObjectId
from app.utils.db import db

router = APIRouter()

BASE_URL = "http://127.0.0.1:8000"


def build_image_url(filename: str) -> str:
    return f"{BASE_URL}/fashion_images/{filename}"


class WishlistItem(BaseModel):
    user_id: str
    outfit_name: str
    outfit_id: str = None         # MongoDB _id from recommendation card — most reliable lookup key
    similarity_score: float = 0.0
    occasion: str = None


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
        outfits_collection  = db["outfits"]

        # ── Already in wishlist? ──────────────────────────────────────────
        existing = wishlist_collection.find_one({
            "user_id":     item.user_id,
            "outfit_name": item.outfit_name,
        })
        if existing:
            return {"success": True, "message": "Already in wishlist"}

        # ── Look up outfit in DB ──────────────────────────────────────────
        # Strategy 1: by _id (most reliable — recommendation engine sends it as "id")
        outfit_doc = None
        if item.outfit_id:
            try:
                outfit_doc = outfits_collection.find_one({"_id": ObjectId(item.outfit_id)})
            except Exception:
                pass  # invalid ObjectId — fall through to name lookup

        # Strategy 2: by name field (mobilenet_service stores name = productDisplayName)
        if not outfit_doc:
            outfit_doc = outfits_collection.find_one({"name": item.outfit_name})

        # Strategy 3: by productDisplayName directly
        if not outfit_doc:
            outfit_doc = outfits_collection.find_one({"productDisplayName": item.outfit_name})

        # ── Build image URL from outfit doc ───────────────────────────────
        if outfit_doc:
            # mobilenet_service uses "filename"; some older scripts use "image_file"
            raw_filename = (
                outfit_doc.get("filename", "")
                or outfit_doc.get("image_file", "")
            )
            image_url       = build_image_url(raw_filename) if raw_filename else None
            outfit_occasion = (
                item.occasion
                or outfit_doc.get("usage", "")
                or outfit_doc.get("occasion", "")
            )
            color    = outfit_doc.get("color",            outfit_doc.get("baseColour", ""))
            category = outfit_doc.get("display_category", outfit_doc.get("category", ""))
            sleeves  = outfit_doc.get("sleeves",          outfit_doc.get("sleeve", ""))
            gender   = outfit_doc.get("gender", "")
        else:
            print(f"⚠️  Outfit not found in DB: name='{item.outfit_name}' id='{item.outfit_id}'")
            image_url       = None
            outfit_occasion = item.occasion or ""
            color = category = sleeves = gender = ""

        # ── Persist ───────────────────────────────────────────────────────
        wishlist_item = {
            "user_id":          item.user_id,
            "outfit_name":      item.outfit_name,
            "outfit_id":        item.outfit_id,
            "similarity_score": item.similarity_score,
            "image_url":        image_url,
            "occasion":         outfit_occasion,
            "color":            color,
            "category":         category,
            "sleeves":          sleeves,
            "gender":           gender,
            "saved_date":       datetime.utcnow(),
        }

        result = wishlist_collection.insert_one(wishlist_item)

        return {
            "success":   True,
            "message":   "Added to wishlist",
            "item_id":   str(result.inserted_id),
            "image_url": image_url,
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
            "user_id":     item.user_id,
            "outfit_name": item.outfit_name,
        })

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Item not found in wishlist")

        return {"success": True, "message": "Removed from wishlist"}

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
        result = wishlist_collection.delete_many({"user_id": data.user_id})
        return {
            "success":       True,
            "message":       f"Cleared {result.deleted_count} items from wishlist",
            "deleted_count": result.deleted_count,
        }
    except Exception as e:
        print(f"Error clearing wishlist: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error clearing wishlist: {str(e)}")


@router.get("/get")
async def get_wishlist(user_id: str):
    """Get all wishlist items for user"""
    try:
        wishlist_collection = db["wishlist"]
        items = list(
            wishlist_collection.find({"user_id": user_id}, {"_id": 0}).sort("saved_date", -1)
        )
        return {"success": True, "user_id": user_id, "items": items, "total": len(items)}
    except Exception as e:
        print(f"Error fetching wishlist: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching wishlist: {str(e)}")


@router.get("/count")
async def get_wishlist_count(user_id: str):
    """Get wishlist count for user"""
    try:
        wishlist_collection = db["wishlist"]
        count = wishlist_collection.count_documents({"user_id": user_id})
        return {"success": True, "user_id": user_id, "count": count}
    except Exception as e:
        print(f"Error getting wishlist count: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")