from fastapi import APIRouter, UploadFile, File
import os, shutil

from app.services.mediapipe_service import extract_landmarks
from app.services.body_shape import classify_body_shape

router = APIRouter(prefix="/recommend", tags=["Recommendation"])

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/")
async def upload_image(file: UploadFile = File(...)):

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # ---- AI PROCESSING ----
    landmarks = extract_landmarks(file_path)
    if landmarks is None:
        return {
            "message": "No body detected",
            "body_shape": None
        }

    body_shape = classify_body_shape(landmarks)

    return {
        "message": "Image processed",
        "body_shape": body_shape,
        "landmarks_count": len(landmarks)
    }
