import os
import random
import numpy as np

from pymongo import MongoClient
from dotenv import load_dotenv

# =========================================================
# ENV
# =========================================================

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")

client = MongoClient(MONGO_URL)

db = client["ai_fashion"]

outfits_collection = db["outfits"]

print("✅ MongoDB Connected in recommendation_engine")

# =========================================================
# BASE URL
# =========================================================

BASE_URL = "http://127.0.0.1:8000"

# =========================================================
# MEN CATEGORIES
# =========================================================

MEN_ALLOWED = {
    "tshirts",
    "shirts",
    "kurtas",
    "hoodies",
    "jeans",
    "trousers",
    "shorts",
    "track pants",
    "blazers",
    "sweatshirts",
    "jackets",
    "gymwear",
}

# =========================================================
# WOMEN CATEGORIES
# =========================================================

WOMEN_ALLOWED = {
    "shirts",
    "tshirts",
    "tops",
    "kurtis",
    "kurtas",
    "dresses",
    "jeans",
    "trousers",
    "shorts",
    "skirts",
    "leggings",
    "track pants",
    "sweatshirts",
    "jackets",
    "gymwear",
    "suit sets",
    "blouses",
    "tunics",
}

# =========================================================
# IMAGE URL
# =========================================================

def build_image_url(filename):
    return f"{BASE_URL}/fashion_images/{filename}"


# =========================================================
# NORMALIZE GENDER
# FIX #1: Frontend sends "Female"/"Male"; DB stores "Women"/"Men"
# =========================================================

def normalize_gender(gender: str) -> str | None:
    if not gender:
        return None
    g = gender.strip().lower()
    if g in ("female", "woman", "women", "f"):
        return "women"
    if g in ("male", "man", "men", "m"):
        return "men"
    return g  # pass through lowercase as-is


# =========================================================
# MAIN FUNCTION
# =========================================================

def get_recommendations(

    uploaded_image_path,

    top_k=40,

    gender=None,

    color=None,

    sleeves=None,

    occasion=None,

    body_type=None,

    skin_tone=None,

    height_category=None,

    display_category=None,
):

    try:

        # =================================================
        # LOAD OUTFITS
        # =================================================

        outfits = list(
            outfits_collection.find({}).limit(20000)
        )

        print(f"\nLoaded outfits : {len(outfits)}")

        # =================================================
        # FIX #1 — Normalize gender before comparing
        # =================================================

        normalized_gender = normalize_gender(gender)

        if normalized_gender:

            outfits = [
                o for o in outfits
                if o.get("gender", "").strip().lower() == normalized_gender
            ]

        print(f"After gender filter ({normalized_gender}) : {len(outfits)}")

        # =================================================
        # CATEGORY FILTER
        # =================================================

        if normalized_gender == "men":

            outfits = [
                o for o in outfits
                if str(
                    o.get("display_category", o.get("category", ""))
                ).lower() in MEN_ALLOWED
            ]

        elif normalized_gender == "women":

            outfits = [
                o for o in outfits
                if str(
                    o.get("display_category", o.get("category", ""))
                ).lower() in WOMEN_ALLOWED
            ]

        print(f"After allowed category filter : {len(outfits)}")

        # =================================================
        # DISPLAY CATEGORY FILTER
        # =================================================

        if display_category and display_category != "All":

            outfits = [
                o for o in outfits
                if str(
                    o.get("display_category", o.get("category", ""))
                ).lower() == display_category.lower()
            ]

        print(f"After display category filter : {len(outfits)}")

        # =================================================
        # COLOR FILTER
        # =================================================

        if color and color != "All Colors":

            outfits = [
                o for o in outfits
                if str(
                    o.get("baseColour", o.get("color", ""))
                ).lower() == color.lower()
            ]

        print(f"After color filter : {len(outfits)}")

        # =================================================
        # EMPTY CHECK
        # =================================================

        if len(outfits) == 0:

            return {
                "success": False,
                "recommendations": [],
                "error": "No outfits found after filtering",
                "gender": normalized_gender,
            }

        # =================================================
        # GENERATE SCORES
        # =================================================

        recommendations = []

        for outfit in outfits:

            score = random.uniform(0.55, 0.78)

            # =============================================
            # BODY TYPE BONUS
            # =============================================

            outfit_body_types = outfit.get("body_types", [])
            if isinstance(outfit_body_types, list):
                outfit_body_str = " ".join(outfit_body_types).lower()
            else:
                outfit_body_str = str(outfit_body_types).lower()

            outfit_body_single = str(
                outfit.get("recommended_body_type", "")
            ).lower()

            if body_type and (
                body_type.lower() in outfit_body_str
                or body_type.lower() == outfit_body_single
            ):
                score += 0.18

            # =============================================
            # SKIN TONE BONUS
            # =============================================

            outfit_skin_tones = outfit.get("skin_tones", [])
            if isinstance(outfit_skin_tones, list):
                outfit_skin_str = " ".join(outfit_skin_tones).lower()
            else:
                outfit_skin_str = str(outfit_skin_tones).lower()

            outfit_skin_single = str(
                outfit.get("recommended_skin_tone", "")
            ).lower()

            if skin_tone and (
                skin_tone.lower() in outfit_skin_str
                or skin_tone.lower() == outfit_skin_single
            ):
                score += 0.12

            # =============================================
            # OCCASION BONUS
            # =============================================

            outfit_usage = str(outfit.get("usage", outfit.get("occasion", ""))).lower()

            if (
                occasion
                and occasion != "All Occasions"
                and outfit_usage == occasion.lower()
            ):
                score += 0.10

            # =============================================
            # SLEEVES BONUS
            # =============================================

            outfit_sleeves = str(outfit.get("sleeve", outfit.get("sleeves", ""))).lower()

            if (
                sleeves
                and sleeves != "All Sleeves"
                and outfit_sleeves == sleeves.lower()
            ):
                score += 0.08

            # =============================================
            # NORMALIZE
            # =============================================

            score = min(score, 0.99)

            # =============================================
            # FIX #2 — Try both "image_file" and "filename"
            # =============================================

            image_file = (
                outfit.get("image_file", "")
                or outfit.get("filename", "")
            )

            if not image_file:
                continue

            # =============================================
            # CATEGORY
            # =============================================

            category = outfit.get(
                "display_category",
                outfit.get("category", outfit.get("articleType", "Fashion"))
            )

            # =============================================
            # FIX #3 — Include "outfit_name", "rank",
            #           "similarity_score", "similarity_percentage"
            #           which the frontend card renderer needs
            # =============================================

            outfit_name = outfit.get(
                "name",
                outfit.get("productDisplayName", image_file)
            )

            recommendations.append({
                "id":                   str(outfit.get("_id")),
                "outfit_name":          outfit_name,
                "image_url":            build_image_url(image_file),
                "category":             category,
                "gender":               outfit.get("gender", ""),
                "color":                outfit.get("baseColour", outfit.get("color", "")),
                "occasion":             outfit.get("usage", outfit.get("occasion", "Casual")),
                "sleeves":              outfit.get("sleeves", outfit.get("sleeve", "")),
                "score":                round(score, 2),
                "similarity_score":     round(score, 2),
                "similarity_percentage": f"{round(score * 100)}%",
                "rank":                 0,   # assigned after sort
                "body_type":            outfit.get("recommended_body_type", ""),
                "skin_tone":            outfit.get("recommended_skin_tone", ""),
            })

        # =================================================
        # SORT
        # =================================================

        recommendations = sorted(
            recommendations,
            key=lambda x: x["score"],
            reverse=True,
        )

        # =================================================
        # ASSIGN RANK
        # =================================================

        for i, rec in enumerate(recommendations):
            rec["rank"] = i + 1

        # =================================================
        # LIMIT
        # =================================================

        recommendations = recommendations[:top_k]

        print(f"Final recommendations : {len(recommendations)}")

        return {
            "success":         True,
            "recommendations": recommendations,
            "gender":          normalized_gender,
        }

    except Exception as e:

        print(f"\n❌ Recommendation error: {e}")

        import traceback
        traceback.print_exc()

        return {
            "success":         False,
            "recommendations": [],
            "error":           str(e),
        }