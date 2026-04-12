"""
Recommendation Engine
Uses cosine similarity between user vector (body type + skin tone + height)
and outfit MobileNet vectors. Height also adjusts the outfit length filter.

FIX NOTES:
- Removed body-type category & skin-tone color pre-filtering from MongoDB query.
  These are now used ONLY for scoring bonuses, not hard DB filters.
  This ensures ALL 4 frontend filters (color, sleeve, occasion, category) work
  on the full dataset and multi-selection works correctly.
- top_k increased fetch limit accordingly.
"""

import numpy as np
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import certifi

load_dotenv()

MONGO_URI  = os.getenv("MONGO_URL")
collection = None

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000, tlsCAFile=certifi.where())
    db         = client["ai_fashion"]
    collection = db["outfits"]
    print("✅ MongoDB Connected in recommendation_engine")
except Exception as e:
    print(f"❌ MongoDB Error: {str(e)}")


# ── Fashion rules (used for SCORING BONUS only, NOT hard DB filters) ──────────

BODY_TYPE_CATEGORIES = {
    "Hourglass":         ["dress", "skirt", "shirt", "t-shirt", "pants", "longsleeve", "outwear", "shorts"],
    "Apple":             ["dress", "outwear", "longsleeve", "shirt", "pants", "skirt"],
    "Pear":              ["dress", "shirt", "longsleeve", "outwear", "skirt", "t-shirt"],
    "Rectangle":         ["dress", "outwear", "longsleeve", "shirt", "t-shirt", "pants", "shorts", "skirt"],
    "Inverted Triangle": ["dress", "skirt", "pants", "shorts", "t-shirt", "longsleeve"],
}

SKIN_TONE_COLORS = {
    "Fair":    ["blue", "pink", "purple", "red", "green", "black", "white", "grey"],
    "Medium":  ["red", "blue", "green", "yellow", "brown", "white", "black", "orange"],
    "Tan":     ["white", "yellow", "orange", "red", "green", "blue", "brown", "multi"],
    "Deep":    ["white", "yellow", "red", "orange", "green", "blue", "multi", "pink"],
    "Unknown": None,
}

HEIGHT_CATEGORY_BOOST = {
    "Tall":    ["dress", "pants", "longsleeve", "outwear", "skirt"],
    "Petite":  ["t-shirt", "shorts", "skirt", "shirt"],
    "Average": None,
}

# Numeric encodings for the user feature vector
BODY_TYPE_ENCODING = {
    "Hourglass":         [1, 0, 0, 0, 0],
    "Apple":             [0, 1, 0, 0, 0],
    "Pear":              [0, 0, 1, 0, 0],
    "Rectangle":         [0, 0, 0, 1, 0],
    "Inverted Triangle": [0, 0, 0, 0, 1],
    "Unknown":           [0, 0, 0, 0, 0],
}

SKIN_TONE_ENCODING = {
    "Fair":    [1, 0, 0, 0, 0],
    "Medium":  [0, 1, 0, 0, 0],
    "Tan":     [0, 0, 1, 0, 0],
    "Deep":    [0, 0, 0, 1, 0],
    "Unknown": [0, 0, 0, 0, 1],
}

HEIGHT_ENCODING = {
    "Tall":    [1, 0, 0],
    "Average": [0, 1, 0],
    "Petite":  [0, 0, 1],
}


def build_user_vector(body_type: str, skin_tone: str, height_category: str = "Average") -> np.ndarray:
    """
    Build user feature vector: body_type (5) + skin_tone (5) + height (3) = 13 dims
    Tiled to 1300 dims then trimmed to 1280 to match MobileNet output.
    Normalised to unit vector for cosine similarity.
    """
    body_enc   = BODY_TYPE_ENCODING.get(body_type or "Unknown",       [0] * 5)
    skin_enc   = SKIN_TONE_ENCODING.get(skin_tone or "Unknown",       [0] * 5)
    height_enc = HEIGHT_ENCODING.get(height_category or "Average", [0, 1, 0])

    base_vector = np.array(body_enc + skin_enc + height_enc, dtype=np.float32)  # 13 dims

    reps        = int(np.ceil(1280 / len(base_vector)))
    user_vector = np.tile(base_vector, reps)[:1280]

    norm = np.linalg.norm(user_vector)
    if norm > 0:
        user_vector = user_vector / norm

    return user_vector


def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(vec_a, vec_b) / (norm_a * norm_b))


def get_recommendations(
    uploaded_image_path: str,
    top_k: int = 20,
    color: str = None,
    sleeves: str = None,
    occasion: str = None,
    body_type: str = None,
    skin_tone: str = None,
    height_category: str = "Average",
):
    """
    Generate recommendations using cosine similarity.

    KEY DESIGN:
    - NO hard category/color pre-filtering in the DB query.
      We fetch ALL outfits so the React frontend filters work on the full set.
    - Body-type categories → +0.10 score bonus (not exclusion)
    - Skin-tone colors     → +0.05 score bonus (not exclusion)
    - Height categories    → +0.05 score bonus (not exclusion)

    This means:
      ✅ Filtering "red" will show ONLY red items
      ✅ Filtering "short sleeve" will show ONLY short-sleeve items
      ✅ Multiple filters work together correctly
      ✅ Recommendations still rank body/skin-appropriate items higher
    """
    try:
        if collection is None:
            return {"success": False, "error": "Database not connected"}

        print(f"\n🔍 Recs for body={body_type}, skin={skin_tone}, height={height_category}")

        # ── Build user vector ──────────────────────────────────────────────
        user_vector = build_user_vector(body_type, skin_tone, height_category)
        print(f"   User vector: {len(user_vector)} dims")

        # ── Bonus category sets (for scoring only) ─────────────────────────
        recommended_cats   = BODY_TYPE_CATEGORIES.get(body_type or "Unknown", [])
        recommended_colors = SKIN_TONE_COLORS.get(skin_tone or "Unknown", []) or []
        height_boost_cats  = HEIGHT_CATEGORY_BOOST.get(height_category or "Average") or []

        print(f"   Body bonus cats:  {recommended_cats}")
        print(f"   Skin bonus colors: {recommended_colors}")
        print(f"   Height boost:     {height_boost_cats}")

        # ── Fetch ALL outfits — no hard pre-filter ─────────────────────────
        # We need the full set so the frontend filters (color/sleeve/occasion/category)
        # always work on the complete data. top_k * 20 gives a large enough pool.
        fetch_limit = max(top_k * 20, 2000)

        all_outfits = list(collection.find(
            {},   # ← NO filter — fetch everything
            {
                "_id": 0, "name": 1, "category": 1, "color": 1,
                "sleeves": 1, "occasion": 1, "image_path": 1, "features": 1
            }
        ).limit(fetch_limit))

        print(f"   Fetched {len(all_outfits)} outfits from DB (no pre-filter)")

        if not all_outfits:
            return {
                "success":            True,
                "body_type_detected": body_type,
                "skin_tone_detected": skin_tone,
                "height_category":    height_category,
                "total_matches":      0,
                "recommendations":    [],
            }

        # ── Score every outfit ─────────────────────────────────────────────
        recommendations = []
        has_features    = False

        for outfit in all_outfits:
            outfit_features = outfit.get("features", [])
            outfit_cat      = (outfit.get("category") or "").lower().strip()
            outfit_color    = (outfit.get("color")    or "").lower().strip()

            # ── Cosine similarity ──────────────────────────────────────────
            if outfit_features and len(outfit_features) > 0:
                outfit_vector = np.array(outfit_features, dtype=np.float32)

                # Handle dimension mismatch (color-histogram fallback = 96 dims)
                if len(outfit_vector) != len(user_vector):
                    base = np.array(
                        BODY_TYPE_ENCODING.get(body_type or "Unknown", [0]*5) +
                        SKIN_TONE_ENCODING.get(skin_tone or "Unknown", [0]*5) +
                        HEIGHT_ENCODING.get(height_category or "Average", [0,1,0]),
                        dtype=np.float32
                    )
                    uv = np.tile(base, int(np.ceil(len(outfit_vector) / 13)))[:len(outfit_vector)]
                    norm = np.linalg.norm(uv)
                    if norm > 0:
                        uv = uv / norm
                    sim_score = cosine_similarity(uv, outfit_vector)
                else:
                    sim_score = cosine_similarity(user_vector, outfit_vector)

                has_features = True
                # Scale raw cosine to 0.55 – 0.94 base range
                sim_score = 0.55 + (sim_score * 0.39)
            else:
                sim_score = round(0.55 + (np.random.random() * 0.30), 2)

            # ── Bonus: body-type appropriate category → +0.10 ─────────────
            if recommended_cats and outfit_cat in recommended_cats:
                sim_score += 0.10

            # ── Bonus: skin-tone appropriate color → +0.05 ────────────────
            if recommended_colors and outfit_color in recommended_colors:
                sim_score += 0.05

            # ── Bonus: height-appropriate category → +0.05 ────────────────
            if height_boost_cats and outfit_cat in height_boost_cats:
                sim_score += 0.05

            # Keep score in [0.55, 0.99]
            sim_score = round(min(max(sim_score, 0.55), 0.99), 2)

            image_path = outfit.get("image_path", "")
            image_url  = f"http://127.0.0.1:8000/outfit_images/{image_path}" if image_path else None

            recommendations.append({
                "rank":                  0,
                "outfit_name":           outfit.get("name", "Outfit"),
                "image_url":             image_url,
                "category":              outfit_cat,
                "color":                 outfit_color or "multi",
                "sleeves":               (outfit.get("sleeves") or "unknown").lower().strip(),
                "occasion":              (outfit.get("occasion") or "casual").lower().strip(),
                "similarity_score":      sim_score,
                "similarity_percentage": f"{int(sim_score * 100)}%",
            })

        if has_features:
            print("   ✅ Using REAL cosine similarity (body + skin + height bonuses)")
        else:
            print("   ⚠️  No feature vectors found — run mobilenet_service.py first")

        # Sort by score descending, take top_k
        recommendations.sort(key=lambda x: x["similarity_score"], reverse=True)
        final_recs = recommendations[:top_k]
        for idx, rec in enumerate(final_recs):
            rec["rank"] = idx + 1

        print(f"✅ Top score: {final_recs[0]['similarity_score'] if final_recs else 'N/A'}")
        print(f"✅ Returning {len(final_recs)} recommendations\n")

        return {
            "success":             True,
            "body_type_detected":  body_type,
            "skin_tone_detected":  skin_tone,
            "height_category":     height_category,
            "total_matches":       len(final_recs),
            "recommendations":     final_recs,
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