"""
bulk_insert_outfits.py
============================================================

Reads:
    fashion_dataset/filtered_images
    fashion_dataset/filtered_styles.csv

and inserts CLEAN fashion products into MongoDB.

ONLY:
✅ Men
✅ Women

NO:
❌ Kids
❌ Boys
❌ Girls
❌ Babywear
❌ Innerwear
❌ Shoes
❌ Accessories
❌ Bags
❌ Rompers
❌ Trunks

============================================================
"""

import os
import cv2
import certifi
import numpy as np
import pandas as pd

from dotenv import load_dotenv
from pymongo import MongoClient
from collections import Counter

# ============================================================
# LOAD ENV
# ============================================================

load_dotenv()

MONGO_URI = os.getenv("MONGO_URL")

if not MONGO_URI:

    print("❌ MONGO_URL missing in .env")

    exit()

# ============================================================
# CONNECT MONGODB
# ============================================================

print("\n🔗 Connecting MongoDB...\n")

client = MongoClient(

    MONGO_URI,

    tlsCAFile=certifi.where(),

    serverSelectionTimeoutMS=30000,
)

db = client["ai_fashion"]

collection = db["outfits"]

print("✅ MongoDB Connected\n")

# ============================================================
# PATHS
# ============================================================

DATASET_FOLDER = "fashion_dataset/filtered_images"

CSV_PATH = "fashion_dataset/filtered_styles.csv"

IMAGE_EXTENSIONS = (

    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
)

# ============================================================
# LOAD CSV
# ============================================================

print("📄 Loading CSV...\n")

try:

    df = pd.read_csv(

        CSV_PATH,

        dtype=str,

        on_bad_lines="skip"
    )

    df = df.fillna("")

    print(f"✅ CSV Loaded : {len(df)} rows\n")

except Exception as e:

    print(f"❌ CSV ERROR: {e}")

    exit()

# ============================================================
# CLEAN COLUMNS
# ============================================================

df.columns = [

    col.strip()

    for col in df.columns
]

# ============================================================
# ALLOWED VALUES
# ============================================================

ALLOWED_GENDER = {

    "Men",
    "Women",
}

ALLOWED_MASTER = {

    "Apparel",
}

# ============================================================
# BLOCKED PRODUCT WORDS
# ============================================================

BLOCKED_WORDS = [

    # kids

    "kids",
    "girls",
    "boys",
    "baby",
    "infant",
    "junior",
    "toddler",

    # innerwear

    "romper",
    "trunk",
    "brief",
    "boxer",
    "bra",
    "lingerie",
    "camisole",
    "nightdress",
    "innerwear",

    # brands

    "gini and jony",
]

# ============================================================
# HARD EXCLUDED
# ============================================================

HARD_EXCLUDED = {

    # shoes

    "Shoes",
    "Casual Shoes",
    "Sports Shoes",
    "Formal Shoes",
    "Heels",
    "Flats",
    "Sandals",
    "Flip Flops",
    "Boots",

    # accessories

    "Bags",
    "Handbags",
    "Wallets",
    "Clutches",
    "Backpacks",
    "Belts",
    "Watches",
    "Jewellery",
    "Caps",
    "Sunglasses",

    # innerwear

    "Bra",
    "Briefs",
    "Boxers",
    "Trunk",
    "Trunks",
    "Innerwear",
    "Innerwear Vests",
    "Shapewear",
    "Lingerie Set",

    # swimwear

    "Swimwear",
    "Bikini",
    "Swimsuit",

    # kids

    "Rompers",
    "Baby Dolls",
}

# ============================================================
# DISPLAY CATEGORY
# ============================================================

MEN_CATEGORY = {

    "Tshirts": "Tshirts",
    "Shirts": "Shirts",
    "Kurtas": "Kurta",
    "Jeans": "Jeans",
    "Trousers": "Trousers",
    "Shorts": "Shorts",
    "Track Pants": "Gymwear",
    "Tracksuits": "Gymwear",
    "Sports Jersey": "Gymwear",
    "Sweatshirts": "Hoodies",
    "Hoodies": "Hoodies",
    "Blazers": "Blazers",
    "Jackets": "Jackets",
}

WOMEN_CATEGORY = {

    "Shirts": "Shirts",
    "Tshirts": "Tshirts",
    "Tops": "Tops",
    "Blouses": "Tops",
    "Tunics": "Tops",

    "Kurtas": "Kurti",
    "Kurtis": "Kurti",
    "Kurta Sets": "Kurti",

    "Suits": "Suit Sets",
    "Suit Sets": "Suit Sets",

    "Jeans": "Jeans",
    "Trousers": "Trousers",
    "Shorts": "Shorts",
    "Skirts": "Skirts",

    "Track Pants": "Gymwear",
    "Tracksuits": "Gymwear",

    "Sweatshirts": "Hoodies",
    "Hoodies": "Hoodies",

    "Jackets": "Jackets",
    "Blazers": "Jackets",

    "Dresses": "Dresses",
}

# ============================================================
# SLEEVE MAPPING
# ============================================================

SLEEVE_MAP = {

    "Tshirts": "short",
    "Tops": "short",
    "Shirts": "long",
    "Kurtas": "long",
    "Kurtis": "long",
    "Sweatshirts": "long",
    "Hoodies": "long",
    "Blazers": "long",
    "Jackets": "long",

    "Jeans": "sleeveless",
    "Trousers": "sleeveless",
    "Shorts": "sleeveless",
    "Skirts": "sleeveless",
}

# ============================================================
# HELPERS
# ============================================================

def parse_id(x):

    try:

        return int(float(str(x)))

    except:

        return None


def get_display_category(gender, article):

    if gender == "Men":

        return MEN_CATEGORY.get(

            article,
            article
        )

    if gender == "Women":

        return WOMEN_CATEGORY.get(

            article,
            article
        )

    return article


def get_sleeve(article):

    return SLEEVE_MAP.get(

        article,
        "short"
    )


def get_body_types(article):

    article = str(article).lower()

    # dresses

    if any(

        x in article

        for x in [

            "dress",
            "kurta",
            "kurti",
            "gown",
        ]
    ):

        return [

            "Hourglass",
            "Pear",
            "Rectangle",
            "Apple",
        ]

    # bottoms

    if any(

        x in article

        for x in [

            "jean",
            "pant",
            "trouser",
            "short",
            "skirt",
        ]
    ):

        return [

            "Pear",
            "Rectangle",
            "Apple",
        ]

    # tops

    return [

        "Hourglass",
        "Rectangle",
        "Apple",
    ]

# ============================================================
# BUILD LOOKUP
# ============================================================

lookup = {}

for _, row in df.iterrows():

    iid = parse_id(row.get("id"))

    if iid:

        lookup[iid] = row

print(f"✅ Metadata Lookup : {len(lookup)}\n")

# ============================================================
# CLEAR OLD DATA
# ============================================================

print("🗑️ Clearing old outfits collection...\n")

collection.delete_many({})

print("✅ Old outfits removed\n")

# ============================================================
# LOAD IMAGES
# ============================================================

if not os.path.exists(DATASET_FOLDER):

    print("❌ filtered_images folder missing")

    exit()

image_files = [

    f for f in os.listdir(DATASET_FOLDER)

    if f.lower().endswith(

        IMAGE_EXTENSIONS
    )
]

print(f"📸 Images Found : {len(image_files)}\n")

# ============================================================
# INSERT LOOP
# ============================================================

inserted = 0

failed = 0

skip_reasons = Counter()

for image_file in image_files:

    try:

        image_id = parse_id(

            image_file.split(".")[0]
        )

        if not image_id:

            skip_reasons["bad_id"] += 1

            continue

        row = lookup.get(image_id)

        if row is None:

            skip_reasons["missing_metadata"] += 1

            continue

        gender = str(

            row.get("gender", "")
        ).strip()

        master = str(

            row.get("masterCategory", "")
        ).strip()

        article = str(

            row.get("articleType", "")
        ).strip()

        product_name = str(

            row.get(
                "productDisplayName",
                ""
            )

        ).lower().strip()

        # ====================================================
        # FILTERS
        # ====================================================

        if gender not in ALLOWED_GENDER:

            skip_reasons["gender"] += 1

            continue

        if master not in ALLOWED_MASTER:

            skip_reasons["master"] += 1

            continue

        if article in HARD_EXCLUDED:

            skip_reasons["excluded_article"] += 1

            continue

        if any(

            word in product_name

            for word in BLOCKED_WORDS
        ):

            skip_reasons["blocked_product"] += 1

            continue

        # ====================================================
        # VALIDATE IMAGE
        # ====================================================

        image_path = os.path.join(

            DATASET_FOLDER,
            image_file
        )

        img = cv2.imread(image_path)

        if img is None:

            skip_reasons["bad_image"] += 1

            continue

        # ====================================================
        # DOCUMENT
        # ====================================================

        doc = {

            "image_id": image_id,

            "name": str(

                row.get(
                    "productDisplayName",
                    image_file
                )
            ),

            "filename": image_file,

            "image_path": image_path,

            "gender": gender,

            "master_category": master,

            "subcategory": str(

                row.get(
                    "subCategory",
                    ""
                )
            ),

            "article_type": article,

            "category": article,

            "display_category":

                get_display_category(
                    gender,
                    article
                ),

            "color": str(

                row.get(
                    "baseColour",
                    "Multi"
                )
            ),

            "base_color": str(

                row.get(
                    "baseColour",
                    "Multi"
                )
            ),

            "season": str(

                row.get(
                    "season",
                    "All"
                )
            ),

            "occasion": str(

                row.get(
                    "usage",
                    "Casual"
                )
            ),

            "usage": str(

                row.get(
                    "usage",
                    "Casual"
                )
            ),

            "sleeves":

                get_sleeve(article),

            "body_types":

                get_body_types(article),

            "skin_tones": [

                "Fair",
                "Light Medium",
                "Medium",
                "Tan",
                "Deep",
            ],

            # feature vector placeholder

            "features":

                np.zeros(1280).tolist(),
        }

        collection.insert_one(doc)

        inserted += 1

        if inserted % 100 == 0:

            print(
                f"✅ Inserted : {inserted}"
            )

    except Exception as e:

        print(
            f"❌ Error : {image_file} -> {e}"
        )

        failed += 1

# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 60)

print("🎉 BULK INSERT COMPLETE")

print("=" * 60)

print(f"Inserted : {inserted}")

print(f"Failed   : {failed}")

print(f"Skipped  : {sum(skip_reasons.values())}")

print("\n📋 Skip Reasons:\n")

for k, v in skip_reasons.items():

    print(f"{k:<25} : {v}")

print("\n📊 MongoDB Counts\n")

print(
    "Men   :",
    collection.count_documents(
        {"gender": "Men"}
    )
)

print(
    "Women :",
    collection.count_documents(
        {"gender": "Women"}
    )
)

print(
    "\n✅ Dataset cleaned successfully"
)

print("=" * 60)