from fastapi import APIRouter
from app.services.recommendation_service import recommend_outfit

router = APIRouter()

@router.get("/recommend")
def get_recommendation(body_type: str, occasion: str):
    outfit = recommend_outfit(body_type, occasion)
    return {"recommended_outfit": outfit}
