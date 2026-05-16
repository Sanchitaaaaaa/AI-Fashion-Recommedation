# ============================================================
# FILE: backend/app/services/recommendation_engine.py
# ============================================================

import os
import numpy as np

from dotenv import load_dotenv
from pymongo import MongoClient

from sklearn.metrics.pairwise import cosine_similarity

from tensorflow.keras.applications.mobilenet_v2 import (
    MobileNetV2,
    preprocess_input
)

from tensorflow.keras.preprocessing import image

from tensorflow.keras.models import Model
from tensorflow.keras.layers import GlobalAveragePooling2D

# ============================================================
# ENV
# ============================================================

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")

# ============================================================
# DB
# ============================================================

client = MongoClient(MONGO_URL)

db = client["ai_fashion"]

outfits_collection = db["outfits"]

print("✅ MongoDB Connected")

# ============================================================
# BASE URL
# ============================================================

BASE_URL = "http://127.0.0.1:8000"

# ============================================================
# MODEL
# ============================================================

print("Loading MobileNetV2...")

base_model = MobileNetV2(

    weights="imagenet",

    include_top=False,

    input_shape=(224, 224, 3)
)

model = Model(

    inputs=base_model.input,

    outputs=GlobalAveragePooling2D()(
        base_model.output
    )
)

print("✅ MobileNet Loaded")

# ============================================================
# ALLOWED CATEGORIES
# ============================================================

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
    "jackets",
    "sweatshirts",
}

WOMEN_ALLOWED = {

    "tops",
    "tshirts",
    "shirts",
    "kurtis",
    "dresses",
    "skirts",
    "jeans",
    "trousers",
    "leggings",
    "shorts",
    "track pants",
    "jackets",
    "sweatshirts",
}

# ============================================================
# FEATURE EXTRACTION
# ============================================================

def extract_features(img_path):

    try:

        img = image.load_img(

            img_path,

            target_size=(224, 224)
        )

        img_array = image.img_to_array(img)

        img_array = np.expand_dims(
            img_array,
            axis=0
        )

        img_array = preprocess_input(
            img_array
        )

        features = model.predict(
            img_array,
            verbose=0
        )[0]

        features = features / np.linalg.norm(
            features
        )

        return features

    except Exception as e:

        print(f"❌ Feature extraction error: {e}")

        return None


# ============================================================
# IMAGE URL
# ============================================================

def build_image_url(filename):

    return f"{BASE_URL}/fashion_images/{filename}"


# ============================================================
# MAIN FUNCTION
# ============================================================

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

        uploaded_features = extract_features(
            uploaded_image_path
        )

        if uploaded_features is None:

            return {

                "success": False,

                "recommendations": [],

                "error":
                    "Feature extraction failed"
            }

        outfits = list(
            outfits_collection.find({})
        )

        print(f"\nLoaded outfits : {len(outfits)}")

        # ====================================================
        # STRICT GENDER FILTER
        # ====================================================

        if gender:

            gender = gender.strip().lower()

            outfits = [

                o for o in outfits

                if str(
                    o.get(
                        "gender",
                        ""
                    )
                ).strip().lower()

                == gender
            ]

        print(
            f"After gender filter : {len(outfits)}"
        )

        # ====================================================
        # REMOVE KIDS PRODUCTS
        # ====================================================

        kids_words = [

            "kids",
            "girls",
            "boys",
            "baby",
            "infant",
        ]

        cleaned = []

        for o in outfits:

            name = str(

                o.get(
                    "productDisplayName",

                    o.get(
                        "name",
                        ""
                    )
                )

            ).lower()

            if any(
                word in name
                for word in kids_words
            ):
                continue

            cleaned.append(o)

        outfits = cleaned

        print(
            f"After kids cleanup : {len(outfits)}"
        )

        # ====================================================
        # CATEGORY FILTER
        # ====================================================

        filtered = []

        for o in outfits:

            category = str(

                o.get(
                    "articleType",

                    o.get(
                        "category",
                        ""
                    )
                )

            ).lower()

            if gender == "men":

                if category in MEN_ALLOWED:
                    filtered.append(o)

            elif gender == "women":

                if category in WOMEN_ALLOWED:
                    filtered.append(o)

        outfits = filtered

        print(
            f"After category filter : {len(outfits)}"
        )

        # ====================================================
        # DISPLAY CATEGORY
        # ====================================================

        if (

            display_category

            and

            display_category != "All Categories"
        ):

            outfits = [

                o for o in outfits

                if str(
                    o.get(
                        "articleType",
                        ""
                    )
                ).lower()

                == display_category.lower()
            ]

        # ====================================================
        # COLOR FILTER
        # ====================================================

        if color and color != "All Colors":

            outfits = [

                o for o in outfits

                if str(
                    o.get(
                        "baseColour",
                        ""
                    )
                ).lower()

                == color.lower()
            ]

        # ====================================================
        # RECOMMENDATIONS
        # ====================================================

        recommendations = []

        for outfit in outfits:

            try:

                embedding = np.array(

                    outfit.get(
                        "embedding",
                        []
                    )
                )

                if len(embedding) == 0:
                    continue

                score = cosine_similarity(

                    [uploaded_features],

                    [embedding]

                )[0][0]

                score = float(score)

                if score < 0.45:
                    continue

                image_file = outfit.get(
                    "image_file",
                    ""
                )

                if not image_file:
                    continue

                recommendations.append({

                    "id":

                        str(
                            outfit.get("_id")
                        ),

                    "outfit_name":

                        outfit.get(
                            "articleType",
                            "Fashion"
                        ),

                    "image_url":

                        build_image_url(
                            image_file
                        ),

                    "category":

                        outfit.get(
                            "articleType",
                            ""
                        ),

                    "gender":

                        outfit.get(
                            "gender",
                            ""
                        ),

                    "color":

                        outfit.get(
                            "baseColour",
                            ""
                        ),

                    "occasion":

                        outfit.get(
                            "usage",
                            ""
                        ),

                    "sleeves":

                        outfit.get(
                            "sleeve",
                            ""
                        ),

                    "similarity_score":

                        round(score, 4),

                    "similarity_percentage":

                        f"{int(score * 100)}%",

                    "rank":

                        len(recommendations) + 1,
                })

            except Exception as e:

                print(f"Skipping item: {e}")

                continue

        recommendations = sorted(

            recommendations,

            key=lambda x:
                x["similarity_score"],

            reverse=True
        )

        recommendations = recommendations[:top_k]

        print(
            f"Final recommendations : "
            f"{len(recommendations)}"
        )

        return {

            "success": True,

            "recommendations":
                recommendations
        }

    except Exception as e:

        print(f"\n❌ Recommendation error: {e}")

        import traceback
        traceback.print_exc()

        return {

            "success": False,

            "recommendations": [],

            "error": str(e)
        }