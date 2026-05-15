"""
bulk_insert_outfits.py
──────────────────────
Reads fashion_dataset/filtered_images + filtered_styles.csv
and inserts clean documents into MongoDB outfits collection.

Run AFTER dataset_filter.py.
Run patch_sleeve_values.py AFTER this if needed.

Key fixes vs old version
──────────────────────────
• Men / Women ONLY — Boys, Girls, Unisex explicitly rejected.
• Removed silent display_category gate that dropped every valid item.
• CSV loaded with dtype=str + strip() — no whitespace/casing issues.
• ID parsed as int(float(x)) — handles '12345.0' from pandas float cols.
• O(1) metadata lookup dict — much faster than repeated df filtering.
• Detailed skip-reason counter — shows exactly why items were skipped.
• Diagnostic block prints actual CSV values before inserting.
"""

import os
import cv2
import numpy as np
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv
import certifi
from collections import Counter

load_dotenv()

# ============================================================
# MONGODB
# ============================================================

MONGO_URI = os.getenv("MONGO_URL")
if not MONGO_URI:
    print("❌  MONGO_URL not set in .env")
    exit(1)

print("Connecting to MongoDB …")
client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=30000,
    connectTimeoutMS=30000,
    tlsCAFile=certifi.where(),
)
db         = client["ai_fashion"]
collection = db["outfits"]
print("✅  MongoDB connected\n")

# ============================================================
# PATHS
# ============================================================

DATASET_PATH = "fashion_dataset/filtered_images"
CSV_PATH     = "fashion_dataset/filtered_styles.csv"

IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp')

# ============================================================
# LOAD METADATA
# ============================================================

try:
    styles_df = pd.read_csv(CSV_PATH, on_bad_lines='skip', dtype=str)
    styles_df = styles_df.apply(
        lambda col: col.str.strip() if col.dtype == "object" else col
    )
    print(f"✅  Loaded metadata : {len(styles_df)} rows\n")
except Exception as e:
    print(f"❌  Failed to load CSV: {e}")
    exit(1)

# ============================================================
# DIAGNOSTIC
# ============================================================

print("=" * 60)
print("📋  CSV DIAGNOSTIC")
print("=" * 60)
print(f"Columns : {styles_df.columns.tolist()}\n")

print("Gender values :")
for val, cnt in styles_df['gender'].value_counts().items():
    marker = "✅" if val in {"Men", "Women"} else "❌ EXCLUDED"
    print(f"  {marker}  {repr(val):<20} → {cnt}")

print("\nmasterCategory values :")
for val, cnt in styles_df['masterCategory'].value_counts().items():
    marker = "✅" if val == "Apparel" else "❌ EXCLUDED"
    print(f"  {marker}  {repr(val):<30} → {cnt}")

print("\nTop 25 articleType values :")
for val, cnt in styles_df['articleType'].value_counts().head(25).items():
    print(f"  {repr(val):<30} → {cnt}")
print("=" * 60 + "\n")

# ============================================================
# FILTER SETS
# ============================================================

ALLOWED_GENDER     = {"Men", "Women"}     # Boys / Girls / Unisex → rejected
ALLOWED_MASTER_CAT = {"Apparel"}

MEN_DISPLAY_CATEGORY = {
    "Tshirts":        "Tshirts",
    "Shirts":         "Shirts",
    "Kurtas":         "Kurtas",
    "Kurta Sets":     "Kurtas",
    "Sweatshirts":    "Hoodies",
    "Hoodies":        "Hoodies",
    "Jeans":          "Jeans",
    "Trousers":       "Trousers",
    "Shorts":         "Shorts",
    "Cargos":         "Trousers",
    "Joggers":        "Trousers",
    "Track Pants":    "Gymwear",
    "Tracksuits":     "Gymwear",
    "Sports Jersey":  "Gymwear",
    "Blazers":        "Blazers",
    "Suits":          "Blazers",
    "Suit Sets":      "Blazers",
    "Nehru Jackets":  "Blazers",
    "Waistcoat":      "Blazers",
    "Jackets":        "Jackets",
    "Windcheater":    "Jackets",
    "Rain Jacket":    "Jackets",
}

WOMEN_DISPLAY_CATEGORY = {
    "Shirts":         "Shirts",
    "Tshirts":        "Tshirts",
    "Tops":           "Tops",
    "Blouses":        "Tops",
    "Tunics":         "Tops",
    "Kurtas":         "Kurti",
    "Kurtis":         "Kurti",
    "Kurta Sets":     "Kurti",
    "Salwar":         "Kurti",
    "Churidar":       "Kurti",
    "Suits":          "Suit Sets",
    "Suit Sets":      "Suit Sets",
    "Sarees":         "Suit Sets",
    "Lehenga Choli":  "Suit Sets",
    "Jeans":          "Jeans",
    "Trousers":       "Trousers",
    "Shorts":         "Shorts",
    "Skirts":         "Skirts",
    "Capris":         "Trousers",
    "Leggings":       "Trousers",
    "Cargos":         "Trousers",
    "Joggers":        "Trousers",
    "Track Pants":    "Gymwear",
    "Tracksuits":     "Gymwear",
    "Sports Jersey":  "Gymwear",
    "Lounge Pants":   "Gymwear",
    "Lounge Shorts":  "Gymwear",
    "Lounge Tshirts": "Gymwear",
    "Dresses":        "Dresses",
    "Jumpsuits":      "Dresses",
    "Dungarees":      "Dresses",
    "Co-ords":        "Dresses",
    "Nightdress":     "Dresses",
    "Jackets":        "Jackets",
    "Blazers":        "Jackets",
    "Sweatshirts":    "Hoodies",
    "Hoodies":        "Hoodies",
    "Shrugs":         "Jackets",
    "Windcheater":    "Jackets",
    "Rain Jacket":    "Jackets",
}

HARD_EXCLUDED = {
    "Shoes", "Casual Shoes", "Sports Shoes", "Formal Shoes",
    "Heels", "Flats", "Sandals", "Flip Flops", "Boots", "Shoe Accessories",
    "Bags", "Handbags", "Wallets", "Clutches", "Backpacks",
    "Trolley Bag", "Messenger Bag", "Laptop Bag", "Travel Accessory",
    "Belts", "Watches", "Jewellery", "Earrings", "Necklace", "Ring",
    "Bracelet", "Pendant", "Brooch", "Anklet",
    "Headwear", "Caps", "Hat", "Sunglasses", "Eyewear",
    "Socks", "Stockings", "Tights",
    "Bra", "Briefs", "Boxers", "Trunk",
    "Innerwear Vests", "Camisoles", "Shapewear",
    "Swimwear", "Bikini", "Swimsuit", "Board Shorts",
    "Bikini Top", "Bikini Bottom", "Lingerie Set",
    "Negligee", "Robe", "Baby Doll", "Suspenders",
    "Thermal Bottoms", "Thermal Tops",
    "Perfume and Body Mist", "Sunscreen", "Lipstick",
    "Nail Polish", "Foundation", "Mascara", "Compact",
    "Kajal and Eyeliner", "Lip Gloss", "Face Moisturisers",
    "Water Bottle", "Umbrellas", "Key chain",
    "Free Gifts", "Sports Accessories", "Vouchers",
}

SLEEVE_MAP = {
    "Tshirts":        "short",
    "Tops":           "short",
    "Sports Jersey":  "short",
    "Lounge Tshirts": "short",
    "Shirts":         "long",
    "Sweatshirts":    "long",
    "Hoodies":        "long",
    "Sweaters":       "long",
    "Jackets":        "long",
    "Blazers":        "long",
    "Suits":          "long",
    "Suit Sets":      "long",
    "Kurtas":         "long",
    "Kurtis":         "long",
    "Kurta Sets":     "long",
    "Tunics":         "long",
    "Blouses":        "long",
    "Shrugs":         "long",
    "Nehru Jackets":  "long",
    "Waistcoat":      "long",
    "Rain Jacket":    "long",
    "Windcheater":    "long",
    "Dresses":        "sleeveless",
    "Sarees":         "sleeveless",
    "Lehenga Choli":  "sleeveless",
    "Jeans":          "sleeveless",
    "Trousers":       "sleeveless",
    "Shorts":         "sleeveless",
    "Skirts":         "sleeveless",
    "Leggings":       "sleeveless",
    "Capris":         "sleeveless",
    "Churidar":       "sleeveless",
    "Salwar":         "sleeveless",
    "Track Pants":    "sleeveless",
    "Tracksuits":     "sleeveless",
    "Lounge Pants":   "sleeveless",
    "Lounge Shorts":  "sleeveless",
    "Cargos":         "sleeveless",
    "Joggers":        "sleeveless",
    "Jumpsuits":      "sleeveless",
    "Dungarees":      "sleeveless",
    "Co-ords":        "sleeveless",
    "Nightdress":     "sleeveless",
}

# ============================================================
# HELPERS
# ============================================================

def get_display_category(gender: str, article_type: str) -> str:
    """Returns display category, falls back to articleType (never drops item)."""
    if gender == "Men":
        return MEN_DISPLAY_CATEGORY.get(article_type, article_type)
    if gender == "Women":
        return WOMEN_DISPLAY_CATEGORY.get(article_type, article_type)
    return article_type


def get_sleeve(article_type: str) -> str:
    return SLEEVE_MAP.get(article_type, "short")


def get_body_types(article_type: str) -> list:
    a = str(article_type).lower()
    if any(x in a for x in ["dress", "kurta", "kurti", "gown", "saree",
                              "lehenga", "jumpsuit", "dungaree", "co-ord"]):
        return ["Hourglass", "Pear", "Rectangle", "Apple"]
    if any(x in a for x in ["jean", "pant", "trouser", "short",
                              "skirt", "legging", "capri", "cargo", "jogger"]):
        return ["Pear", "Rectangle", "Apple"]
    if any(x in a for x in ["shirt", "top", "blouse", "tshirt", "t-shirt",
                              "sweater", "jacket", "coat", "sweatshirt",
                              "hoodie", "blazer", "suit", "waistcoat"]):
        return ["Hourglass", "Rectangle", "Apple"]
    return ["Hourglass", "Pear", "Rectangle", "Apple"]


def parse_id(raw) -> int | None:
    try:
        return int(float(str(raw).strip()))
    except (ValueError, TypeError):
        return None


# ============================================================
# BUILD FAST LOOKUP  id(int) → row
# ============================================================

id_to_row = {}
for _, row in styles_df.iterrows():
    iid = parse_id(row.get('id', ''))
    if iid is not None:
        id_to_row[iid] = row

print(f"📋  Metadata lookup built : {len(id_to_row)} entries\n")

# ============================================================
# CLEAR OLD DATA
# ============================================================

print("🗑️  Clearing existing outfits collection …")
result = collection.delete_many({})
print(f"✅  Deleted {result.deleted_count} documents\n")

# ============================================================
# GET IMAGE FILES
# ============================================================

if not os.path.exists(DATASET_PATH):
    print(f"❌  Folder not found: {DATASET_PATH}")
    print("   Run dataset_filter.py first.")
    exit(1)

image_files = sorted([
    f for f in os.listdir(DATASET_PATH)
    if f.lower().endswith(IMAGE_EXTENSIONS)
])
print(f"📁  Found {len(image_files)} images in {DATASET_PATH}\n")

# ============================================================
# INSERT LOOP
# ============================================================

total        = 0
failed       = 0
skip_reasons = Counter()

for img_filename in image_files:

    img_path = os.path.join(DATASET_PATH, img_filename)

    try:
        # ── Parse image ID ────────────────────────────────
        image_id = parse_id(img_filename.split('.')[0])
        if image_id is None:
            skip_reasons["bad_filename"] += 1
            continue

        # ── Match metadata ────────────────────────────────
        row = id_to_row.get(image_id)
        if row is None:
            skip_reasons["no_metadata"] += 1
            continue

        # ── Read fields ───────────────────────────────────
        gender       = str(row.get('gender',         '')).strip()
        master_cat   = str(row.get('masterCategory', '')).strip()
        article_type = str(row.get('articleType',    '')).strip()

        # ── Men / Women ONLY ──────────────────────────────
        if gender not in ALLOWED_GENDER:
            skip_reasons[f"excluded_gender={repr(gender)}"] += 1
            continue

        # ── masterCategory filter ─────────────────────────
        if master_cat not in ALLOWED_MASTER_CAT:
            skip_reasons[f"masterCat={repr(master_cat)}"] += 1
            continue

        # ── Hard exclusion ────────────────────────────────
        if article_type in HARD_EXCLUDED:
            skip_reasons[f"hardExcluded={article_type}"] += 1
            continue

        # ── Verify image is readable ──────────────────────
        img_data = cv2.imread(img_path)
        if img_data is None:
            skip_reasons["unreadable_image"] += 1
            continue

        # ── Display category (fallback = articleType) ─────
        display_cat = get_display_category(gender, article_type)

        # ── Build document ────────────────────────────────
        doc = {
            "image_id"        : image_id,
            "name"            : str(row.get('productDisplayName', img_filename)).strip(),
            "filename"        : img_filename,
            "image_path"      : img_path,

            "gender"          : gender,          # "Men" or "Women" ONLY

            "master_category" : master_cat,
            "subcategory"     : str(row.get('subCategory', '')).strip(),
            "article_type"    : article_type,

            "category"        : article_type,
            "display_category": display_cat,

            "color"           : str(row.get('baseColour', 'Multi')).strip(),
            "base_color"      : str(row.get('baseColour', 'Multi')).strip(),
            "season"          : str(row.get('season', 'All')).strip(),
            "occasion"        : str(row.get('usage', 'Casual')).strip(),
            "usage"           : str(row.get('usage', 'Casual')).strip(),

            "sleeves"         : get_sleeve(article_type),
            "body_types"      : get_body_types(article_type),
            "skin_tones"      : ["Fair", "Light Medium", "Medium", "Tan", "Deep"],

            "features"        : np.zeros(1280).tolist(),
        }

        collection.insert_one(doc)
        total += 1

        if total % 100 == 0:
            print(f"   ✅  Inserted {total} outfits …")

    except Exception as e:
        print(f"❌  Error on {img_filename}: {e}")
        failed += 1

# ============================================================
# SUMMARY
# ============================================================

count       = collection.count_documents({})
men_count   = collection.count_documents({"gender": "Men"})
women_count = collection.count_documents({"gender": "Women"})

print("\n" + "=" * 60)
print("🎉  BULK INSERT COMPLETE")
print("=" * 60)
print(f"Total inserted       : {total}")
print(f"Failed (errors)      : {failed}")
print(f"Total docs in DB     : {count}")
print(f"  Men   in DB        : {men_count}")
print(f"  Women in DB        : {women_count}")

total_skipped = sum(skip_reasons.values())
if total_skipped:
    print(f"\n⚠️  Skipped {total_skipped} — breakdown:")
    for reason, cnt in skip_reasons.most_common():
        print(f"   {reason:<45} → {cnt}")
else:
    print("\n✅  Zero images skipped!")

print("\n📊  Display category breakdown:")
pipeline = [
    {"$group": {
        "_id": {"gender": "$gender", "display_category": "$display_category"},
        "count": {"$sum": 1}
    }},
    {"$sort": {"_id.gender": 1, "_id.display_category": 1}}
]
for doc in collection.aggregate(pipeline):
    g   = doc["_id"]["gender"]
    cat = doc["_id"]["display_category"]
    cnt = doc["count"]
    print(f"  [{g:<6}] {cat:<20} → {cnt}")

sample = collection.find_one({})
if sample:
    print("\n📝  Sample document:")
    for key in ("name", "gender", "category", "display_category",
                "subcategory", "color", "occasion", "sleeves"):
        print(f"  {key:<20}: {sample.get(key)}")

print("=" * 60)
print("\n▶  Next step: python patch_sleeve_values.py")