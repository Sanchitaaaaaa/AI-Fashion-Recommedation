from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
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

UPLOAD_DIR = Path("storage/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def upload_image(file: UploadFile = File(...), user_id: str = None):
    """Upload and analyze user image"""
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")

        image_id = str(uuid.uuid4())
        file_extension = Path(file.filename).suffix
        saved_filename = f"{image_id}{file_extension}"
        file_path = UPLOAD_DIR / saved_filename

        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        print(f"✅ File saved: {file_path}")

        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image file")

        # ── Step 1: body analysis (also returns raw_landmarks) ────────────────
        body_analysis = analyze_body_measurements(image)
        raw_landmarks = body_analysis.pop("raw_landmarks", None)   # extract, don't store
        print(f"✅ Body analysis done: {body_analysis['body_type']} / {body_analysis['height_category']}")

        # ── Step 2: skin tone — pass landmarks for accurate face crop ─────────
        skin_analysis = analyze_skin_tone(image, raw_landmarks=raw_landmarks)
        print(f"✅ Skin tone done: {skin_analysis['skin_tone']}")

        # ── Step 3: store to MongoDB ──────────────────────────────────────────
        user_id = user_id or "default_user"

        user_images_collection = db["user_images"]
        image_doc = {
            "image_id":   image_id,
            "user_id":    user_id,
            "file_path":  str(file_path),
            "file_name":  file.filename,
            "uploaded_at": datetime.utcnow(),
            "file_size":  len(contents),
        }
        user_images_collection.insert_one(image_doc)

        user_features_collection = db["user_features"]
        features_doc = {
            "image_id":  image_id,
            "user_id":   user_id,
            **body_analysis,
            **skin_analysis,
            "created_at": datetime.utcnow(),
        }
        user_features_collection.insert_one(features_doc)
        print(f"✅ Features saved to MongoDB: {image_id}")

        # ── Step 4: return everything the frontend needs ──────────────────────
        return {
            "success":               True,
            "message":               "Image uploaded and analyzed successfully",
            "imageId":               image_id,
            "fileName":              file.filename,
            "file_path":             str(file_path),
            # body
            "body_type":             body_analysis.get("body_type"),
            "body_type_confidence":  body_analysis.get("body_type_confidence", 0.0),
            "height_category":       body_analysis.get("height_category", "Average"),
            # skin
            "skin_tone":             skin_analysis.get("skin_tone"),
            "skin_tone_confidence":  skin_analysis.get("skin_tone_confidence", 0.0),
            # raw ratios (optional — useful for debugging in frontend)
            "features":              body_analysis.get("features", {}),
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
        features = db["user_features"].find_one({"image_id": image_id}, {"_id": 0})
        if not features:
            raise HTTPException(status_code=404, detail="Features not found")
        return {"success": True, "features": features}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/images/{user_id}")
async def get_user_images(user_id: str):
    """Get all images for a user"""
    try:
        images = list(db["user_images"].find(
            {"user_id": user_id}, {"_id": 0}
        ).sort("uploaded_at", -1))
        return {"success": True, "user_id": user_id, "images": images, "total": len(images)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/images/detail/{image_id}")
async def get_image_detail(image_id: str):
    try:
        image = db["user_images"].find_one({"image_id": image_id}, {"_id": 0})
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")
        return {"success": True, "image": image}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/image-file/{image_id}")
async def get_image_file(image_id: str):
    """Serve the actual image file for display"""
    try:
        image_doc = db["user_images"].find_one({"image_id": image_id}, {"_id": 0})
        if not image_doc:
            raise HTTPException(status_code=404, detail="Image not found")
        fp = Path(image_doc["file_path"])
        if not fp.exists():
            raise HTTPException(status_code=404, detail="Image file not found on disk")
        return FileResponse(str(fp), media_type="image/jpeg")
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.delete("/images/{image_id}")
async def delete_image(image_id: str):
    try:
        image_doc = db["user_images"].find_one({"image_id": image_id})
        if image_doc and "file_path" in image_doc:
            fp = Path(image_doc["file_path"])
            if fp.exists():
                fp.unlink()
        db["user_images"].delete_one({"image_id": image_id})
        db["user_features"].delete_one({"image_id": image_id})
        return {"success": True, "message": "Image deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/user/{user_id}")
async def get_user_profile(user_id: str):
    try:
        users_collection = db["users"]
        user = users_collection.find_one({"user_id": user_id}, {"_id": 0})
        if not user:
            user_doc = {"user_id": user_id, "created_at": datetime.utcnow()}
            users_collection.insert_one(user_doc)
            user = user_doc
        image_count = db["user_images"].count_documents({"user_id": user_id})
        return {"success": True, "user": user, "image_count": image_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/user/{user_id}")
async def update_user_profile(user_id: str, data: dict):
    try:
        db["users"].update_one(
            {"user_id": user_id},
            {"$set": {**data, "updated_at": datetime.utcnow()}},
            upsert=True
        )
        return {"success": True, "message": "User profile updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")