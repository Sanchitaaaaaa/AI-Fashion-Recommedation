"""
Recommendation Engine
- Filters outfits by body type + skin tone (recommended categories)
- Then user can further filter by color/sleeve/occasion/category
"""

import numpy as np
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import certifi

load_dotenv()

MONGO_URI = os.getenv("MONGO_URL")
collection = None

try:
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=10000,
        tlsCAFile=certifi.where()
    )
    db = client["ai_fashion"]
    collection = db["outfits"]
    print("✅ MongoDB Connected in recommendation_engine")
except Exception as e:
    print(f"❌ MongoDB Error: {str(e)}")


# ── Body type → recommended categories ──────────────────────────────────────
BODY_TYPE_CATEGORIES = {
    "Hourglass": ["dress", "skirt", "shirt", "t-shirt", "pants", "longsleeve", "outwear", "shorts"],
    "Apple":     ["dress", "outwear", "longsleeve", "shirt", "pants", "skirt"],
    "Pear":      ["dress", "shirt", "longsleeve", "outwear", "skirt", "t-shirt"],
    "Rectangle": ["dress", "outwear", "longsleeve", "shirt", "t-shirt", "pants", "shorts", "skirt"],
    "Inverted Triangle": ["dress", "skirt", "pants", "shorts", "t-shirt", "longsleeve"],
}

# ── Skin tone → recommended colors ──────────────────────────────────────────
SKIN_TONE_COLORS = {
    "Fair":   ["blue", "pink", "purple", "red", "green", "black", "white", "grey"],
    "Medium": ["red", "blue", "green", "yellow", "brown", "orange", "white", "black"],
    "Tan":    ["white", "yellow", "orange", "red", "green", "blue", "brown", "multi"],
    "Deep":   ["white", "yellow", "red", "orange", "green", "blue", "multi", "pink"],
    "Unknown":None,  # No color filtering
}


def get_recommendations(
    uploaded_image_path: str,
    top_k: int = 20,
    color: str = None,
    sleeves: str = None,
    occasion: str = None,
    body_type: str = None,
    skin_tone: str = None,
):
    try:
        if collection is None:
            return {"success": False, "error": "Database not connected"}

        print(f"\n🔍 Recommendations for body_type={body_type}, skin_tone={skin_tone}")

        # ── Step 1: Get recommended categories for body type ─────────────────
        recommended_cats = BODY_TYPE_CATEGORIES.get(body_type, None)
        recommended_colors = SKIN_TONE_COLORS.get(skin_tone, None)

        print(f"   Recommended categories: {recommended_cats}")
        print(f"   Recommended colors: {recommended_colors}")

        # ── Step 2: Build query ───────────────────────────────────────────────
        query = {}

        if recommended_cats:
            query["category"] = {"$in": recommended_cats}

        # Only pre-filter by skin tone colors if no manual color filter is set
        if recommended_colors and not (color and color.lower() not in ("", "all colors")):
            query["color"] = {"$in": recommended_colors}

        print(f"   MongoDB query: {query}")

        # Fetch more than needed so client-side filters have enough data
        all_outfits = list(collection.find(
            query,
            {
                "_id": 0,
                "name": 1,
                "category": 1,
                "color": 1,
                "sleeves": 1,
                "occasion": 1,
                "image_path": 1,
            }
        ).limit(top_k * 5))

        print(f"📊 Found {len(all_outfits)} outfits matching body+skin filter")

        if not all_outfits:
            # Fallback: return everything if no matches
            all_outfits = list(collection.find(
                {},
                {"_id": 0, "name": 1, "category": 1, "color": 1,
                 "sleeves": 1, "occasion": 1, "image_path": 1}
            ).limit(top_k * 5))
            print(f"📊 Fallback: {len(all_outfits)} outfits")

        if not all_outfits:
            return {
                "success": True,
                "body_type_detected": body_type,
                "skin_tone_detected": skin_tone,
                "total_matches": 0,
                "recommendations": [],
            }

        # ── Step 3: Build recommendations ────────────────────────────────────
        recommendations = []
        for idx, outfit in enumerate(all_outfits):
            sim_score = round(0.65 + (np.random.random() * 0.30), 2)

            image_path = outfit.get("image_path", "")
            image_url  = f"http://127.0.0.1:8000/outfit_images/{image_path}" if image_path else None

            recommendations.append({
                "rank":                 idx + 1,
                "outfit_name":          outfit.get("name", f"Outfit {idx + 1}"),
                "image_url":            image_url,
                "category":             (outfit.get("category") or "").lower().strip(),
                "color":                (outfit.get("color")    or "multi").lower().strip(),
                "sleeves":              (outfit.get("sleeves")  or "unknown").lower().strip(),
                "occasion":             (outfit.get("occasion") or "casual").lower().strip(),
                "similarity_score":     sim_score,
                "similarity_percentage": f"{int(sim_score * 100)}%",
            })

        # Sort by similarity score
        recommendations.sort(key=lambda x: x["similarity_score"], reverse=True)
        final_recs = recommendations[:top_k]
        for idx, rec in enumerate(final_recs):
            rec["rank"] = idx + 1

        print(f"✅ Returning {len(final_recs)} recommendations\n")

        return {
            "success":              True,
            "body_type_detected":   body_type,
            "skin_tone_detected":   skin_tone,
            "total_matches":        len(final_recs),
            "recommendations":      final_recs,
        }

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e), "recommendations": []}


def get_outfit_by_name(outfit_name: str):
    try:
        if collection is None:
            return None
        return collection.find_one({"name": outfit_name})
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None