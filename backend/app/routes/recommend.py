from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.recommendation_engine import get_recommendations
from typing import Optional

router = APIRouter()


class RecommendationRequest(BaseModel):
    image_id:         str
    top_k:            int = 20
    gender:           Optional[str] = None
    color:            Optional[str] = None
    sleeves:          Optional[str] = None
    occasion:         Optional[str] = None
    display_category: Optional[str] = None
    body_type:        Optional[str] = None
    skin_tone:        Optional[str] = None
    height_category:  Optional[str] = "Average"


# ── sanitise helpers ──────────────────────────────────────────────────────────

# FIX: expanded ignore set, and now lowercases before comparing
_IGNORE_VALUES = {
    "", "all", "all colors", "all colours", "all sleeves",
    "all occasions", "all categories", "all tabs", "none", "null",
}

def _clean(val: Optional[str]) -> Optional[str]:
    """
    Return None for any 'All …' placeholder so the DB filter is skipped
    and all matching documents are returned.

    Note: display_category is NOT cleaned through here — tab values like
    "Tshirts", "Jeans" are real filter values, not placeholders.
    Only pass it through _clean if the frontend explicitly sends "All".
    """
    if val is None:
        return None
    stripped = val.strip()
    if stripped.lower() in _IGNORE_VALUES:
        return None
    return stripped


# ── routes ────────────────────────────────────────────────────────────────────

@router.post("/generate")
async def generate_recommendations(request: RecommendationRequest):
    """Generate gender-aware outfit recommendations."""
    try:
        print("\n📥 Incoming recommendation request:")
        print(f"   gender           = {request.gender!r}")
        print(f"   body_type        = {request.body_type!r}")
        print(f"   skin_tone        = {request.skin_tone!r}")
        print(f"   color            = {request.color!r}")
        print(f"   sleeves          = {request.sleeves!r}")
        print(f"   occasion         = {request.occasion!r}")
        print(f"   display_category = {request.display_category!r}")
        print(f"   top_k            = {request.top_k}")

        # display_category: only suppress if it's a genuine "show all" sentinel
        cleaned_display = _clean(request.display_category)

        result = get_recommendations(
            uploaded_image_path = request.image_id,
            top_k               = request.top_k,
            gender              = _clean(request.gender),
            color               = _clean(request.color),
            sleeves             = _clean(request.sleeves),
            occasion            = _clean(request.occasion),
            display_category    = cleaned_display,
            body_type           = request.body_type,
            skin_tone           = request.skin_tone,
            height_category     = request.height_category or "Average",
        )
        return result

    except Exception as e:
        print(f"❌ Recommend route error: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}


@router.get("/status")
async def get_status():
    try:
        from app.utils.db import db
        total  = db["outfits"].count_documents({})
        men    = db["outfits"].count_documents({"gender": "Men"})
        women  = db["outfits"].count_documents({"gender": "Women"})
        return {
            "success":       True,
            "total_outfits": total,
            "men_outfits":   men,
            "women_outfits": women,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/test")
async def test():
    return {"status": "ok", "message": "Recommendations route working"}


@router.get("/debug")
async def debug():
    """
    Hit GET /recommend/debug to verify DB state before debugging the frontend.
    Shows total counts, display_category breakdown, feature check, and samples.
    Remove before going to production.
    """
    try:
        from app.utils.db import db
        col = db["outfits"]

        total  = col.count_documents({})
        men    = col.count_documents({"gender": "Men"})
        women  = col.count_documents({"gender": "Women"})

        # Sample one Men doc and one Women doc
        sample_men   = col.find_one({"gender": "Men"},   {"_id": 0, "features": 0})
        sample_women = col.find_one({"gender": "Women"}, {"_id": 0, "features": 0})

        # display_category breakdown
        pipeline = [
            {"$group": {
                "_id": {"gender": "$gender", "display_category": "$display_category"},
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id.gender": 1, "_id.display_category": 1}}
        ]
        cat_breakdown = [
            {
                "gender":           d["_id"].get("gender"),
                "display_category": d["_id"].get("display_category"),
                "count":            d["count"],
            }
            for d in col.aggregate(pipeline)
        ]

        # Check if display_category is missing entirely
        missing_display_cat = col.count_documents(
            {"display_category": {"$exists": False}}
        )
        null_display_cat = col.count_documents(
            {"display_category": None}
        )

        # Check if features are real or placeholder zeros
        feature_check = None
        doc_with_features = col.find_one(
            {"features": {"$exists": True, "$not": {"$size": 0}}},
            {"features": 1, "_id": 0}
        )
        if doc_with_features:
            feats    = doc_with_features.get("features", [])
            non_zero = sum(1 for f in feats if f != 0.0)
            feature_check = {
                "feature_dims":    len(feats),
                "non_zero_values": non_zero,
                "is_placeholder":  non_zero == 0,
                "advice": (
                    "✅ Real MobileNet features present"
                    if non_zero > 0
                    else "⚠️  Features are all-zero placeholders — run mobilenet_service.py"
                ),
            }

        return {
            "db_counts": {
                "total": total,
                "men":   men,
                "women": women,
            },
            "display_category_issues": {
                "missing_field":  missing_display_cat,
                "null_value":     null_display_cat,
                "advice": (
                    "✅ All docs have display_category"
                    if missing_display_cat == 0 and null_display_cat == 0
                    else f"⚠️  {missing_display_cat + null_display_cat} docs missing display_category — run patch_sleeve_values.py"
                ),
            },
            "feature_check":      feature_check,
            "category_breakdown": cat_breakdown,
            "sample_men_doc":     sample_men,
            "sample_women_doc":   sample_women,
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}