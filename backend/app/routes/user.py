from fastapi import APIRouter, UploadFile, File, Form
import uuid
import os
from app.services.mediapipe_service import analyze_body
from app.utils.db import users_collection

router = APIRouter()

UPLOAD_DIR = "backend/storage/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_photo(
    file: UploadFile = File(...),
    occasion: str = Form(...)
):
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, file_id + ".jpg")

    with open(file_path, "wb") as f:
        f.write(await file.read())

    body_data = analyze_body(file_path)

    if not body_data:
        return {"error": "No human detected"}

    user_data = {
        "photo_path": file_path,
        "occasion": occasion,
        **body_data
    }

    users_collection.insert_one(user_data)

    return user_data
