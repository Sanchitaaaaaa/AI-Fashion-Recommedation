from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
from datetime import datetime
import uuid
import os
from pathlib import Path
from app.utils.db import db
from app.services.mediapipe_service import analyze_body_measurements
from app.services.skin_tone_service import analyze_skin_tone
import cv2
import numpy as np

router = APIRouter()

# Create uploads folder if it doesn't exist
UPLOAD_DIR = Path("storage/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

class UserImage(BaseModel):
    user_id: str
    image_id: str
    file_path: str
    uploaded_at: datetime

@router.post("/upload")
async def upload_image(file: UploadFile = File(...), user_id: str = None):
    """Upload and analyze user image"""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Generate unique image ID
        image_id = str(uuid.uuid4())
        file_extension = Path(file.filename).suffix
        saved_filename = f"{image_id}{file_extension}"
        file_path = UPLOAD_DIR / saved_filename
        
        # Read file content
        contents = await file.read()
        
        # Save file to disk
        with open(file_path, "wb") as f:
            f.write(contents)
        
        print(f"✅ File saved: {file_path}")
        
        # Convert bytes to numpy array for analysis
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        # Analyze body measurements
        body_analysis = analyze_body_measurements(image)
        print(f"✅ Body analysis: {body_analysis}")
        
        # Analyze skin tone
        skin_analysis = analyze_skin_tone(image)
        print(f"✅ Skin analysis: {skin_analysis}")
        
        # Prepare features to store
        features = {
            **body_analysis,
            **skin_analysis,
        }
        
        # Store image metadata in MongoDB
        user_id = user_id or "default_user"
        
        user_images_collection = db["user_images"]
        image_doc = {
            "image_id": image_id,
            "user_id": user_id,
            "file_path": str(file_path),
            "file_name": file.filename,
            "uploaded_at": datetime.utcnow(),
            "file_size": len(contents),
        }
        
        image_result = user_images_collection.insert_one(image_doc)
        print(f"✅ Image metadata saved to MongoDB: {image_id}")
        
        # Store features in MongoDB
        user_features_collection = db["user_features"]
        features_doc = {
            "image_id": image_id,
            "user_id": user_id,
            **features,
            "created_at": datetime.utcnow(),
        }
        
        features_result = user_features_collection.insert_one(features_doc)
        print(f"✅ Features saved to MongoDB: {image_id}")
        
        return {
            "success": True,
            "message": "Image uploaded and analyzed successfully",
            "imageId": image_id,
            "fileName": file.filename,
            "body_type": body_analysis.get("body_type"),
            "skin_tone": skin_analysis.get("skin_tone"),
            "body_type_confidence": body_analysis.get("body_type_confidence", 0.85),
            "skin_tone_confidence": skin_analysis.get("skin_tone_confidence", 0.85),
        }
    
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"❌ Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/features/{image_id}")
async def get_image_features(image_id: str):
    """Get extracted features for an image"""
    try:
        user_features_collection = db["user_features"]
        
        features = user_features_collection.find_one(
            {"image_id": image_id},
            {"_id": 0}
        )
        
        if not features:
            raise HTTPException(status_code=404, detail="Features not found for this image")
        
        return {
            "success": True,
            "features": features,
        }
    
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"❌ Error fetching features: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/images/{user_id}")
async def get_user_images(user_id: str):
    """Get all images for a user"""
    try:
        user_images_collection = db["user_images"]
        
        images = list(user_images_collection.find(
            {"user_id": user_id},
            {"_id": 0}
        ).sort("uploaded_at", -1))
        
        return {
            "success": True,
            "user_id": user_id,
            "images": images,
            "total": len(images),
        }
    
    except Exception as e:
        print(f"❌ Error fetching images: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/images/detail/{image_id}")
async def get_image_detail(image_id: str):
    """Get details for a specific image"""
    try:
        user_images_collection = db["user_images"]
        
        image = user_images_collection.find_one(
            {"image_id": image_id},
            {"_id": 0}
        )
        
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")
        
        return {
            "success": True,
            "image": image,
        }
    
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"❌ Error fetching image detail: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.delete("/images/{image_id}")
async def delete_image(image_id: str):
    """Delete an image"""
    try:
        user_images_collection = db["user_images"]
        user_features_collection = db["user_features"]
        
        # Find and delete image file
        image_doc = user_images_collection.find_one({"image_id": image_id})
        if image_doc and "file_path" in image_doc:
            file_path = Path(image_doc["file_path"])
            if file_path.exists():
                file_path.unlink()
                print(f"✅ File deleted: {file_path}")
        
        # Delete from MongoDB
        user_images_collection.delete_one({"image_id": image_id})
        user_features_collection.delete_one({"image_id": image_id})
        
        print(f"✅ Image deleted from MongoDB: {image_id}")
        
        return {
            "success": True,
            "message": "Image deleted successfully",
        }
    
    except Exception as e:
        print(f"❌ Error deleting image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/user/{user_id}")
async def get_user_profile(user_id: str):
    """Get user profile"""
    try:
        users_collection = db["users"]
        
        user = users_collection.find_one(
            {"user_id": user_id},
            {"_id": 0}
        )
        
        if not user:
            # Create new user if doesn't exist
            user_doc = {
                "user_id": user_id,
                "created_at": datetime.utcnow(),
            }
            users_collection.insert_one(user_doc)
            user = user_doc
        
        # Get user images count
        user_images_collection = db["user_images"]
        image_count = user_images_collection.count_documents({"user_id": user_id})
        
        return {
            "success": True,
            "user": user,
            "image_count": image_count,
        }
    
    except Exception as e:
        print(f"❌ Error fetching user profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/user/{user_id}")
async def update_user_profile(user_id: str, data: dict):
    """Update user profile"""
    try:
        users_collection = db["users"]
        
        update_data = {
            **data,
            "updated_at": datetime.utcnow(),
        }
        
        result = users_collection.update_one(
            {"user_id": user_id},
            {"$set": update_data},
            upsert=True
        )
        
        return {
            "success": True,
            "message": "User profile updated",
        }
    
    except Exception as e:
        print(f"❌ Error updating user profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")