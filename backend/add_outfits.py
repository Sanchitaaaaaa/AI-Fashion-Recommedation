"""
add_outfits.py
──────────────
Adds Myntra fashion dataset outfits to MongoDB (with base64 image encoding).
Use this script if your recommendation route serves images directly from DB.

For large datasets prefer bulk_insert_outfits.py (no base64, faster).

Filters applied:
  ✅  gender        : Men / Women only
  ✅  masterCategory: Apparel only
  ✅  subCategory   : clothing subcats only
  ✅  articleType   : explicit exclusion list
"""

import os
import base64
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# MONGODB
# ============================================================

MONGO_URL = os.getenv("MONGO_URL")
if not MONGO_URL:
    print("❌  MONGO_URL not set in .env")
    exit(1)

print("Connecting to MongoDB...")
client = MongoClient(MONGO_URL)
db     = client["ai_fashion"]
print("✅  MongoDB connected\n")

# ============================================================
# PATHS
# ============================================================

IMAGE_FOLDER = "fashion_dataset/filtered_images"
CSV_PATH     = "fashion_dataset/filtered_styles.csv"

IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp']

# ============================================================
# FILTER SETS  (keep in sync with dataset_filter.py)
# ============================================================

ALLOWED_GENDER = {"Men", "Women"}

ALLOWED_MASTER_CAT = {"Apparel"}

ALLOWED_SUBCATEGORY = {
    "Topwear",
    "Bottomwear",
    "Dress",
    "Saree",
    "Suits",
    "Loungewear and Nightwear",
    "Innerwear",
}

EXCLUDED_ARTICLE_TYPES = {
    "Shoes", "Casual Shoes", "Sports Shoes", "Formal Shoes",
    "Heels", "Flats", "Sandals", "Flip Flops", "Boots",
    "Belts", "Bags", "Handbags", "Wallets", "Clutches",
    "Watches", "Jewellery", "Earrings", "Necklace", "Ring",
    "Headwear", "Caps", "Hat",
    "Socks", "Stockings", "Tights",
    "Perfume and Body Mist", "Sunscreen", "Lipstick",
    "Backpacks", "Trolley Bag", "Travel Accessory",
    "Water Bottle", "Umbrellas", "Key chain",
}

# ============================================================
# HELPERS
# ============================================================

def encode_image_to_base64(path: str):
    try:
        with open(path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        print(f"  ❌  Encode error: {e}")
        return None


def load_metadata():
    try:
        df = pd.read_csv(CSV_PATH, on_bad_lines='skip')
        print(f"✅  Loaded metadata: {len(df)} rows")
        return df
    except Exception as e:
        print(f"❌  Failed to load CSV: {e}")
        exit(1)


def get_all_images():
    if not os.path.exists(IMAGE_FOLDER):
        print(f"❌  Image folder not found: {IMAGE_FOLDER}")
        return []
    return [
        {"filename": f, "filepath": os.path.join(IMAGE_FOLDER, f)}
        for f in sorted(os.listdir(IMAGE_FOLDER))
        if os.path.isfile(os.path.join(IMAGE_FOLDER, f))
        and any(f.lower().endswith(ext) for ext in IMAGE_EXTENSIONS)
    ]


def get_body_types(article_type: str) -> list:
    a = str(article_type).lower()
    if any(x in a for x in ["dress", "kurta", "gown", "saree"]):
        return ["hourglass", "pear", "rectangle", "apple"]
    if any(x in a for x in ["jeans", "pants", "trousers",
                              "shorts", "skirt", "leggings"]):
        return ["pear", "rectangle", "apple"]
    if any(x in a for x in ["shirt", "top", "blouse",
                              "t-shirt", "tshirt", "sweater",
                              "jacket", "coat", "sweatshirt"]):
        return ["hourglass", "rectangle", "apple"]
    return ["hourglass", "pear", "rectangle", "apple"]

# ============================================================
# MAIN
# ============================================================

styles_df   = load_metadata()
image_files = get_all_images()

if not image_files:
    print("❌  No images found!")
    exit(1)

print(f"✅  Found {len(image_files)} images\n")

outfits_collection = db["outfits"]

inserted_count = 0
skipped_count  = 0

for image_info in image_files:

    filename = image_info["filename"]
    filepath = image_info["filepath"]

    try:
        image_id  = int(filename.split('.')[0])
        row_match = styles_df[styles_df['id'] == image_id]

        if row_match.empty:
            skipped_count += 1
            continue

        row = row_match.iloc[0]

        gender       = str(row.get('gender', '')).strip()
        master_cat   = str(row.get('masterCategory', '')).strip()
        sub_cat      = str(row.get('subCategory', '')).strip()
        article_type = str(row.get('articleType', '')).strip()

        # ── Filters ───────────────────────────────────────
        if gender not in ALLOWED_GENDER:
            skipped_count += 1
            continue

        if master_cat not in ALLOWED_MASTER_CAT:
            skipped_count += 1
            continue

        if sub_cat not in ALLOWED_SUBCATEGORY:
            skipped_count += 1
            continue

        if article_type in EXCLUDED_ARTICLE_TYPES:
            skipped_count += 1
            continue

        # ── Avoid duplicates ──────────────────────────────
        if outfits_collection.find_one({"filename": filename}):
            print(f"  ⚠️  Already exists: {filename}")
            skipped_count += 1
            continue

        # ── Encode image ──────────────────────────────────
        image_data = encode_image_to_base64(filepath)
        if not image_data:
            skipped_count += 1
            continue

        # ── Build document ────────────────────────────────
        outfit = {
            "name"           : str(row.get('productDisplayName', filename)),
            "filename"       : filename,
            "image"          : image_data,
            "image_path"     : filepath,

            "gender"         : gender,          # "Men" or "Women"

            "master_category": master_cat,
            "subcategory"    : sub_cat,
            "article_type"   : article_type,

            # Aliases
            "type"           : article_type,
            "category"       : article_type,
            "color"          : str(row.get('baseColour', 'Multi')),
            "base_color"     : str(row.get('baseColour', 'Multi')),
            "season"         : str(row.get('season', 'All')),
            "occasion"       : str(row.get('usage', 'Casual')),
            "usage"          : str(row.get('usage', 'Casual')),

            "body_types"     : get_body_types(article_type),
            "skin_tones"     : ["fair", "medium", "tan", "deep"],

            "features"       : [0.0] * 512,
        }

        outfits_collection.insert_one(outfit)
        inserted_count += 1
        print(f"  ✅  {filename} | {gender} | {article_type}")

    except Exception as e:
        print(f"  ❌  Error on {filename}: {e}")
        skipped_count += 1

# ============================================================
# SUMMARY
# ============================================================

total       = outfits_collection.count_documents({})
men_count   = outfits_collection.count_documents({"gender": "Men"})
women_count = outfits_collection.count_documents({"gender": "Women"})

print("\n" + "=" * 60)
print("🎉  DATASET IMPORT COMPLETE")
print("=" * 60)
print(f"Total in DB  : {total}")
print(f"  Men        : {men_count}")
print(f"  Women      : {women_count}")
print(f"Inserted now : {inserted_count}")
print(f"Skipped      : {skipped_count}")
print("=" * 60)