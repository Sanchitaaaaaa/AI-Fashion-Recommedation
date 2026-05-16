# ============================================================
# FILE: backend/app/routes/recommend.py
# ============================================================

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from app.services.recommendation_engine import (
    get_recommendations
)

router = APIRouter()


# ============================================================
# REQUEST MODEL
# ============================================================

class RecommendationRequest(BaseModel):

    image_id: str

    top_k: int = 40

    gender: Optional[str] = None

    color: Optional[str] = None

    sleeves: Optional[str] = None

    occasion: Optional[str] = None

    display_category: Optional[str] = None

    body_type: Optional[str] = None

    skin_tone: Optional[str] = None

    height_category: Optional[str] = "Average"


# ============================================================
# CLEAN HELPERS
# ============================================================

_IGNORE_VALUES = {

    "",
    "all",
    "all colors",
    "all sleeves",
    "all occasions",
    "all categories",
    "none",
    "null",
}


def _clean(value):

    if value is None:
        return None

    value = str(value).strip()

    if value.lower() in _IGNORE_VALUES:
        return None

    return value


# ============================================================
# GENERATE RECOMMENDATIONS
# ============================================================

@router.post("/generate")

async def generate_recommendations(

    request: RecommendationRequest
):

    try:

        print("\n============================")
        print("📥 RECOMMEND REQUEST")
        print("============================")

        print(f"Gender           : {request.gender}")
        print(f"Body Type        : {request.body_type}")
        print(f"Skin Tone        : {request.skin_tone}")
        print(f"Color            : {request.color}")
        print(f"Sleeves          : {request.sleeves}")
        print(f"Occasion         : {request.occasion}")
        print(f"Display Category : {request.display_category}")

        result = get_recommendations(

            uploaded_image_path=
                request.image_id,

            top_k=
                request.top_k,

            gender=
                _clean(request.gender),

            color=
                _clean(request.color),

            sleeves=
                _clean(request.sleeves),

            occasion=
                _clean(request.occasion),

            display_category=
                _clean(request.display_category),

            body_type=
                request.body_type,

            skin_tone=
                request.skin_tone,

            height_category=
                request.height_category,
        )

        print(
            f"\n✅ Recommendations Returned : "
            f"{len(result.get('recommendations', []))}"
        )

        return result

    except Exception as e:

        print(f"\n❌ Recommend Route Error: {e}")

        import traceback
        traceback.print_exc()

        return {

            "success": False,

            "recommendations": [],

            "error": str(e)
        }


# ============================================================
# STATUS
# ============================================================

@router.get("/status")

async def status():

    try:

        from app.utils.db import db

        total = db["outfits"].count_documents({})

        men = db["outfits"].count_documents({

            "gender": "Men"
        })

        women = db["outfits"].count_documents({

            "gender": "Women"
        })

        return {

            "success": True,

            "total_outfits": total,

            "men_outfits": men,

            "women_outfits": women,
        }

    except Exception as e:

        return {

            "success": False,

            "error": str(e)
        }