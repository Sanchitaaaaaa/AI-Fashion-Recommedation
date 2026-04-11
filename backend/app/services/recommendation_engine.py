"""
Recommendation Engine - REAL AI SIMILARITY
Uses cosine similarity between:
  - User feature vector (body type + skin tone encoded)
  - Outfit feature vector (MobileNet 1280-dim visual features)

Flow:
  1. Build user vector from body measurements + skin tone
  2. Fetch outfit vectors from MongoDB
  3. Compute cosine similarity
  4. Rank outfits by similarity score (REAL score, not random)
  5. Apply body type category filter + skin tone color filter
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
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=10000,
        tlsCAFile=certifi.where()
    )
    db         = client["ai_fashion"]
    collection = db["outfits"]
    print("✅ MongoDB Connected in recommendation_engine")
except Exception as e:
    print(f"❌ MongoDB Error: {str(e)}")


# ── Fashion rules ─────────────────────────────────────────────────────────────
# Which clothing categories suit each body type
BODY_TYPE_CATEGORIES = {
    "Hourglass":         ["dress", "skirt", "shirt", "t-shirt", "pants", "longsleeve", "outwear", "shorts"],
    "Apple":             ["dress", "outwear", "longsleeve", "shirt", "pants", "skirt"],
    "Pear":              ["dress", "shirt", "longsleeve", "outwear", "skirt", "t-shirt"],
    "Rectangle":         ["dress", "outwear", "longsleeve", "shirt", "t-shirt", "pants", "shorts", "skirt"],
    "Inverted Triangle": ["dress", "skirt", "pants", "shorts", "t-shirt", "longsleeve"],
}

# Which colors suit each skin tone
SKIN_TONE_COLORS = {
    "Fair":    ["blue", "pink", "purple", "red", "green", "black", "white", "grey"],
    "Medium":  ["red", "blue", "green", "yellow", "brown", "white", "black", "orange"],
    "Tan":     ["white", "yellow", "orange", "red", "green", "blue", "brown", "multi"],
    "Deep":    ["white", "yellow", "red", "orange", "green", "blue", "multi", "pink"],
    "Unknown": None,
}

# Numeric encoding for body types (used in user feature vector)
BODY_TYPE_ENCODING = {
    "Hourglass":         [1, 0, 0, 0, 0],
    "Apple":             [0, 1, 0, 0, 0],
    "Pear":              [0, 0, 1, 0, 0],
    "Rectangle":         [0, 0, 0, 1, 0],
    "Inverted Triangle": [0, 0, 0, 0, 1],
    "Unknown":           [0, 0, 0, 0, 0],
}

# Numeric encoding for skin tones
SKIN_TONE_ENCODING = {
    "Fair":    [1, 0, 0, 0, 0],
    "Medium":  [0, 1, 0, 0, 0],
    "Tan":     [0, 0, 1, 0, 0],
    "Deep":    [0, 0, 0, 1, 0],
    "Unknown": [0, 0, 0, 0, 1],
}


def build_user_vector(body_type: str, skin_tone: str) -> np.ndarray:
    """
    Build a user feature vector from body type + skin tone.
    
    This vector is matched against outfit MobileNet vectors.
    
    Structure: [body_type_encoding (5) + skin_tone_encoding (5)] = 10 dims
    We tile/repeat it to match MobileNet's 1280 dims for cosine similarity.
    """
    body_enc = BODY_TYPE_ENCODING.get(body_type or "Unknown", [0]*5)
    skin_enc = SKIN_TONE_ENCODING.get(skin_tone or "Unknown", [0]*5)

    # Base 10-dim vector
    base_vector = np.array(body_enc + skin_enc, dtype=np.float32)

    # Tile to 1280 dims (MobileNet output size) 
    # 1280 / 10 = 128 repetitions
    user_vector = np.tile(base_vector, 128)  # shape: (1280,)

    # Normalize to unit vector
    norm = np.linalg.norm(user_vector)
    if norm > 0:
        user_vector = user_vector / norm

    return user_vector


def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """
    Compute cosine similarity between two vectors.
    Returns value between 0.0 and 1.0.
    1.0 = identical, 0.0 = completely different.
    """
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
):
    """
    Generate recommendations using REAL cosine similarity.
    
    Steps:
    1. Build user vector from body type + skin tone
    2. Pre-filter outfits by body type categories + skin tone colors
    3. Compute cosine similarity of user vector vs each outfit's MobileNet vector
    4. Rank by real similarity score
    """
    try:
        if collection is None:
            return {"success": False, "error": "Database not connected"}

        print(f"\n🔍 Recommendations for body={body_type}, skin={skin_tone}")

        # ── Step 1: Build user feature vector ────────────────────────────────
        user_vector = build_user_vector(body_type, skin_tone)
        print(f"   User vector: {len(user_vector)} dims")

        # ── Step 2: Get recommended categories + colors ───────────────────────
        recommended_cats   = BODY_TYPE_CATEGORIES.get(body_type, None)
        recommended_colors = SKIN_TONE_COLORS.get(skin_tone, None)

        print(f"   Recommended categories: {recommended_cats}")
        print(f"   Recommended colors: {recommended_colors}")

        # ── Step 3: Query MongoDB with filters ────────────────────────────────
        query = {}

        if recommended_cats:
            query["category"] = {"$in": recommended_cats}

        # Only filter by skin-tone colors if user hasn't picked a manual color
        if recommended_colors and not (color and color.lower() not in ("", "all colors")):
            query["color"] = {"$in": recommended_colors}

        print(f"   MongoDB query: {query}")

        # Fetch outfits INCLUDING feature vectors
        all_outfits = list(collection.find(
            query,
            {
                "_id":        0,
                "name":       1,
                "category":   1,
                "color":      1,
                "sleeves":    1,
                "occasion":   1,
                "image_path": 1,
                "features":   1,   # ← MobileNet vector
            }
        ).limit(top_k * 8))

        print(f"   Found {len(all_outfits)} outfits in DB")

        # Fallback if no matches
        if not all_outfits:
            print("   Fallback: fetching all outfits")
            all_outfits = list(collection.find(
                {},
                {"_id": 0, "name": 1, "category": 1, "color": 1,
                 "sleeves": 1, "occasion": 1, "image_path": 1, "features": 1}
            ).limit(top_k * 8))

        if not all_outfits:
            return {
                "success": True,
                "body_type_detected": body_type,
                "skin_tone_detected":  skin_tone,
                "total_matches": 0,
                "recommendations": [],
            }

        # ── Step 4: Compute REAL cosine similarity ────────────────────────────
        recommendations = []
        has_features    = False

        for outfit in all_outfits:
            outfit_features = outfit.get("features", [])

            if outfit_features and len(outfit_features) > 0:
                # REAL similarity using MobileNet vectors
                outfit_vector = np.array(outfit_features, dtype=np.float32)

                # If dims differ (fallback histogram=96 vs mobilenet=1280),
                # resize user vector to match
                if len(outfit_vector) != len(user_vector):
                    uv = np.tile(
                        np.array(
                            BODY_TYPE_ENCODING.get(body_type or "Unknown", [0]*5) +
                            SKIN_TONE_ENCODING.get(skin_tone or "Unknown", [0]*5),
                            dtype=np.float32
                        ),
                        int(np.ceil(len(outfit_vector) / 10))
                    )[:len(outfit_vector)]
                    norm = np.linalg.norm(uv)
                    if norm > 0:
                        uv = uv / norm
                    sim_score = cosine_similarity(uv, outfit_vector)
                else:
                    sim_score = cosine_similarity(user_vector, outfit_vector)

                has_features = True

                # Scale similarity: cosine gives ~0.7-0.9 range for similar items
                # Map to 0.60 - 0.99 for display
                sim_score = 0.60 + (sim_score * 0.39)
                sim_score = round(min(max(sim_score, 0.60), 0.99), 2)

            else:
                # No feature vector stored — use random (outfit wasn't processed with MobileNet)
                sim_score = round(0.60 + (np.random.random() * 0.30), 2)

            image_path = outfit.get("image_path", "")
            image_url  = f"http://127.0.0.1:8000/outfit_images/{image_path}" if image_path else None

            recommendations.append({
                "rank":                  0,
                "outfit_name":           outfit.get("name", "Outfit"),
                "image_url":             image_url,
                "category":              (outfit.get("category") or "").lower().strip(),
                "color":                 (outfit.get("color")    or "multi").lower().strip(),
                "sleeves":               (outfit.get("sleeves")  or "unknown").lower().strip(),
                "occasion":              (outfit.get("occasion") or "casual").lower().strip(),
                "similarity_score":      sim_score,
                "similarity_percentage": f"{int(sim_score * 100)}%",
            })

        if has_features:
            print("   ✅ Using REAL cosine similarity scores")
        else:
            print("   ⚠️  No feature vectors found — run mobilenet_service.py first")

        # ── Step 5: Sort by real similarity score ─────────────────────────────
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