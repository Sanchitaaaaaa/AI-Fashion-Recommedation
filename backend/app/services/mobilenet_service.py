"""
MobileNet Fashion Feature Extractor  v3.0
──────────────────────────────────────────
Processes filtered_images, extracts MobileNetV2 features (1280-d),
and inserts/updates MongoDB with strict filters aligned to dataset_filter.py.

Category display groups:
  MEN   : Tshirts, Shirts, Kurtas, Hoodies, Jeans, Trousers, Shorts,
           Gymwear, Blazers, Jackets
  WOMEN : Shirts, Tshirts, Tops, Kurti, Suit Sets, Jeans, Trousers,
           Shorts, Skirts, Gymwear, Dresses, Jackets, Hoodies

Run this INSTEAD OF bulk_insert_outfits.py when you want real AI
feature vectors (not placeholder zeros).
"""

import os
import cv2
import certifi
import numpy as np
import pandas as pd

from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# ═══════════════════════════════════════════════════════════════
# MONGODB
# ═══════════════════════════════════════════════════════════════

MONGO_URI = os.getenv("MONGO_URL")

client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=10000,
    tlsCAFile=certifi.where(),
)
db         = client["ai_fashion"]
collection = db["outfits"]

# ═══════════════════════════════════════════════════════════════
# DATASET PATHS
# ═══════════════════════════════════════════════════════════════

IMAGE_FOLDER = "fashion_dataset/filtered_images"
CSV_PATH     = "fashion_dataset/filtered_styles.csv"

# ═══════════════════════════════════════════════════════════════
# FILTER SETS  (keep in sync with bulk_insert_outfits.py)
# ═══════════════════════════════════════════════════════════════

ALLOWED_GENDER     = {"Men", "Women"}
ALLOWED_MASTER_CAT = {"Apparel"}

HARD_EXCLUDED = {
    "Shoes", "Casual Shoes", "Sports Shoes", "Formal Shoes",
    "Heels", "Flats", "Sandals", "Flip Flops", "Boots",
    "Belts", "Bags", "Handbags", "Wallets", "Clutches",
    "Watches", "Jewellery", "Earrings", "Necklace", "Ring",
    "Headwear", "Caps", "Hat",
    "Socks", "Stockings", "Tights",
    "Perfume and Body Mist", "Sunscreen", "Lipstick",
    "Backpacks", "Trolley Bag", "Travel Accessory",
    "Water Bottle", "Umbrellas", "Key chain",
    "Bra", "Briefs", "Boxers", "Trunk",
    "Innerwear Vests", "Camisoles", "Shapewear",
    "Swimwear", "Bikini", "Board Shorts",
    "Lingerie Set", "Negligee", "Robe", "Baby Doll",
}

# ═══════════════════════════════════════════════════════════════
# DISPLAY CATEGORY MAPS
# ═══════════════════════════════════════════════════════════════

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

# ═══════════════════════════════════════════════════════════════
# SLEEVE MAP
# ═══════════════════════════════════════════════════════════════

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

# ═══════════════════════════════════════════════════════════════
# BODY TYPES
# ═══════════════════════════════════════════════════════════════

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

# ═══════════════════════════════════════════════════════════════
# DISPLAY CATEGORY HELPER
# ═══════════════════════════════════════════════════════════════

def get_display_category(gender: str, article_type: str) -> str:
    if gender == "Men":
        return MEN_DISPLAY_CATEGORY.get(article_type, article_type)
    if gender == "Women":
        return WOMEN_DISPLAY_CATEGORY.get(article_type, article_type)
    return article_type

def get_sleeve(article_type: str) -> str:
    return SLEEVE_MAP.get(article_type, "short")

# ═══════════════════════════════════════════════════════════════
# LOAD CSV
# ═══════════════════════════════════════════════════════════════

try:
    styles_df = pd.read_csv(CSV_PATH, on_bad_lines='skip')
    print(f"✅ Loaded metadata: {len(styles_df)} rows")
except Exception as e:
    print(f"❌ Failed loading CSV: {e}")
    exit(1)

# ═══════════════════════════════════════════════════════════════
# LOAD MOBILENET
# ═══════════════════════════════════════════════════════════════

print("Loading MobileNetV2...")
try:
    import tensorflow as tf

    base_model = tf.keras.applications.MobileNetV2(
        weights="imagenet",
        include_top=False,
        pooling="avg",
        input_shape=(224, 224, 3),
    )
    base_model.trainable = False
    USE_MOBILENET = True
    print("✅ MobileNetV2 loaded (1280-d features)")

except Exception as e:
    print(f"⚠️  MobileNet unavailable: {e}")
    USE_MOBILENET = False

# ═══════════════════════════════════════════════════════════════
# IMAGE PRE-PROCESSING
# Resize to exactly 224×224 with padding to preserve aspect ratio
# — better quality for feature extraction than simple squash.
# ═══════════════════════════════════════════════════════════════

def preprocess_image(img_bgr: np.ndarray) -> np.ndarray:
    """
    Letterbox-resize to 224×224, convert to RGB, apply MobileNetV2
    preprocessing.  Returns (1, 224, 224, 3) float32 tensor.
    """
    h, w = img_bgr.shape[:2]
    scale = 224 / max(h, w)
    new_h, new_w = int(h * scale), int(w * scale)

    resized  = cv2.resize(img_bgr, (new_w, new_h),
                          interpolation=cv2.INTER_LANCZOS4)

    canvas   = np.zeros((224, 224, 3), dtype=np.uint8)
    y_off    = (224 - new_h) // 2
    x_off    = (224 - new_w) // 2
    canvas[y_off:y_off + new_h, x_off:x_off + new_w] = resized

    rgb      = cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)
    tensor   = tf.keras.applications.mobilenet_v2.preprocess_input(
                    rgb.astype(np.float32))
    return np.expand_dims(tensor, axis=0)

# ═══════════════════════════════════════════════════════════════
# FEATURE EXTRACTION
# ═══════════════════════════════════════════════════════════════

def extract_features(image_path: str) -> list:
    try:
        img = cv2.imread(image_path)
        if img is None:
            return []

        tensor   = preprocess_image(img)
        features = base_model.predict(tensor, verbose=0).flatten()

        norm = np.linalg.norm(features)
        if norm > 0:
            features = features / norm

        return features.tolist()

    except Exception as e:
        print(f"  ⚠️  Feature error: {e}")
        return []

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def process_images():
    image_files = sorted([
        f for f in os.listdir(IMAGE_FOLDER)
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
    ])

    print(f"\n📁 Found {len(image_files)} images\n")

    outfits  = []
    skipped  = 0
    failed   = 0

    for i, filename in enumerate(image_files):
        image_path = os.path.join(IMAGE_FOLDER, filename)
        print(f"[{i+1}/{len(image_files)}] {filename}", end=" … ")

        try:
            image_id  = int(filename.split('.')[0])
            row_match = styles_df[styles_df['id'] == image_id]

            if row_match.empty:
                print("❌ metadata missing")
                skipped += 1
                continue

            row = row_match.iloc[0]

            gender       = str(row.get('gender',         '')).strip()
            master_cat   = str(row.get('masterCategory', '')).strip()
            article_type = str(row.get('articleType',    '')).strip()

            # ── Hard filters ──────────────────────────────────
            if gender not in ALLOWED_GENDER:
                skipped += 1
                print(f"⏭ skip (gender={gender})")
                continue

            if master_cat not in ALLOWED_MASTER_CAT:
                skipped += 1
                print(f"⏭ skip (cat={master_cat})")
                continue

            if article_type in HARD_EXCLUDED:
                skipped += 1
                print(f"⏭ skip (excluded={article_type})")
                continue

            display_cat = get_display_category(gender, article_type)
            all_known   = (set(MEN_DISPLAY_CATEGORY.keys()) |
                           set(WOMEN_DISPLAY_CATEGORY.keys()))
            if article_type not in all_known:
                skipped += 1
                print(f"⏭ skip (unmapped={article_type})")
                continue

            # ── Extract features ───────────────────────────────
            if USE_MOBILENET:
                features = extract_features(image_path)
            else:
                features = np.zeros(1280).tolist()

            if not features:
                print("❌ feature extraction failed")
                failed += 1
                continue

            outfit = {
                "image_id"        : image_id,
                "name"            : str(row.get('productDisplayName', filename)),
                "filename"        : filename,
                "image_path"      : image_path,
                "gender"          : gender,
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
                "features"        : features,
            }

            outfits.append(outfit)
            print(f"✅ {gender} | {display_cat} | {outfit['occasion']} | {len(features)}d")

        except Exception as e:
            print(f"❌ {e}")
            failed += 1

    print(f"\n📊 Processed: {len(outfits)}  |  Skipped: {skipped}  |  Failed: {failed}")

    if not outfits:
        print("⚠️  Nothing to insert.")
        return

    men_count   = sum(1 for o in outfits if o["gender"] == "Men")
    women_count = sum(1 for o in outfits if o["gender"] == "Women")
    print(f"\n   Men:   {men_count}")
    print(f"   Women: {women_count}")

    # ── Clear and re-insert ───────────────────────────────────────────────
    print("\n🗑️  Clearing old outfits…")
    collection.delete_many({})

    print("💾  Inserting into MongoDB…\n")
    batch_size = 50
    for i in range(0, len(outfits), batch_size):
        collection.insert_many(outfits[i:i + batch_size])
        print(f"   ✅ Batch {i // batch_size + 1} done")

    # ── Indexes ───────────────────────────────────────────────────────────
    collection.create_index("gender")
    collection.create_index("display_category")
    collection.create_index("occasion")
    collection.create_index("color")
    print("✅ Indexes created")

    # ── Final counts ──────────────────────────────────────────────────────
    total    = collection.count_documents({})
    men_db   = collection.count_documents({"gender": "Men"})
    women_db = collection.count_documents({"gender": "Women"})

    print("\n" + "=" * 60)
    print("🎉  MOBILENET PROCESSING COMPLETE")
    print("=" * 60)
    print(f"Total inserted : {total}")
    print(f"  Men          : {men_db}")
    print(f"  Women        : {women_db}")
    print(f"Feature dims   : {len(outfits[0]['features'])}")

    print("\n📊  Display category breakdown:")
    from collections import Counter
    all_docs = list(collection.find({}, {"_id": 0, "gender": 1, "display_category": 1}))
    cnt = Counter((d["gender"], d.get("display_category", "?")) for d in all_docs)
    for (g, cat), n in sorted(cnt.items()):
        print(f"  [{g:<6}] {cat:<20} → {n}")

    print("=" * 60)


if __name__ == "__main__":
    process_images()