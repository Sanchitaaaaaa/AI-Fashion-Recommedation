from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.recommendation_engine import get_recommendations
from typing import Optional

router = APIRouter()

class RecommendationRequest(BaseModel):
    """Request model"""
    image_id: str
    top_k: int = 20
    color: Optional[str] = None
    sleeves: Optional[str] = None
    occasion: Optional[str] = None
    body_type: Optional[str] = None
    skin_tone: Optional[str] = None


@router.post("/generate")
async def generate_recommendations(request: RecommendationRequest):
    """Generate outfit recommendations"""
    
    try:
        # Call recommendation engine
        result = get_recommendations(
            uploaded_image_path=request.image_id,
            top_k=request.top_k,
            color=request.color,
            sleeves=request.sleeves,
            occasion=request.occasion,
            body_type=request.body_type,
            skin_tone=request.skin_tone
        )
        
        return result
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/status")
async def get_status():
    """Get system status"""
    try:
        from app.utils.db import db
        count = db["outfits"].count_documents({})
        return {
            "success": True,
            "total_outfits": count
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/test")
async def test():
    """Test endpoint"""
    return {"status": "ok", "message": "Recommendations working"}