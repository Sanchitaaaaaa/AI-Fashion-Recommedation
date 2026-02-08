from fastapi import APIRouter, UploadFile, File

router = APIRouter(prefix="/recommend", tags=["Recommendation"])

@router.post("/")
async def upload_image(file: UploadFile = File(...)):
    return {"filename": file.filename}
