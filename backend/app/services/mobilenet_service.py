"""
Outfit Processor - Extracts REAL MobileNet feature vectors from images
These vectors capture visual style, texture, shape of each outfit.
Stored in MongoDB and used for real cosine similarity scoring.

FIX NOTES:
- SLEEVE_MAP corrected: t-shirt → "short", shirt → "long", longsleeve → "long"
  dress/skirt/pants/shorts/hat/shoes → "sleeveless" (no arm coverage)
- OCCASION_MAP: outwear → "casual" (was already correct)
- Re-run this script after fixing to re-populate MongoDB with correct sleeve values.
"""

import os
import numpy as np
from pymongo import MongoClient
from dotenv import load_dotenv
import certifi
import cv2

load_dotenv()

MONGO_URI   = os.getenv("MONGO_URL")
client      = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000, tlsCAFile=certifi.where())
db          = client["ai_fashion"]
collection  = db["outfits"]

BASE_FOLDER = "outfit_images"

# ── Load MobileNet ────────────────────────────────────────────────────────────
print("Loading MobileNet model...")
try:
    import tensorflow as tf
    base_model = tf.keras.applications.MobileNetV2(
        weights="imagenet",
        include_top=False,
        pooling="avg",
        input_shape=(224, 224, 3)
    )
    base_model.trainable = False
    print("✅ MobileNetV2 loaded")
    USE_MOBILENET = True
except Exception as e:
    print(f"⚠️  MobileNet not available: {e}")
    print("   Will use color histogram as fallback feature vector")
    USE_MOBILENET = False


# ── Feature extraction ────────────────────────────────────────────────────────
def extract_mobilenet_features(image_path: str) -> list:
    try:
        img = cv2.imread(image_path)
        if img is None:
            return []
        img = cv2.resize(img, (224, 224))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = tf.keras.applications.mobilenet_v2.preprocess_input(img)
        img = np.expand_dims(img, axis=0)
        features = base_model.predict(img, verbose=0).flatten()
        norm = np.linalg.norm(features)
        if norm > 0:
            features = features / norm
        return features.tolist()
    except Exception as e:
        print(f"   ⚠️  Feature extraction error: {e}")
        return []


def extract_color_histogram_features(image_path: str) -> list:
    try:
        img = cv2.imread(image_path)
        if img is None:
            return []
        img = cv2.resize(img, (100, 100))
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h_hist = cv2.calcHist([hsv], [0], None, [32], [0, 180]).flatten()
        s_hist = cv2.calcHist([hsv], [1], None, [32], [0, 256]).flatten()
        v_hist = cv2.calcHist([hsv], [2], None, [32], [0, 256]).flatten()
        features = np.concatenate([h_hist, s_hist, v_hist])
        norm = np.linalg.norm(features)
        if norm > 0:
            features = features / norm
        return features.tolist()
    except Exception as e:
        print(f"   ⚠️  Histogram error: {e}")
        return []


def extract_features(image_path: str) -> list:
    if USE_MOBILENET:
        return extract_mobilenet_features(image_path)
    return extract_color_histogram_features(image_path)


# ── Color detection ───────────────────────────────────────────────────────────
COLOR_RANGES = [
    ("red",    0,   10),
    ("orange", 11,  20),
    ("yellow", 21,  35),
    ("green",  36,  85),
    ("blue",   86, 130),
    ("purple", 131,160),
    ("pink",   161,170),
    ("red",    171,180),
]

def detect_color_from_image(image_path: str) -> str:
    try:
        img = cv2.imread(image_path)
        if img is None:
            return "multi"
        img = cv2.resize(img, (100, 100))
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        s = hsv[:, :, 1]
        v = hsv[:, :, 2]
        mask = (s > 40) & (v > 40) & (v < 240)
        if np.sum(mask) < 50:
            mean_v = float(np.mean(v))
            if mean_v > 180:   return "white"
            elif mean_v < 60:  return "black"
            else:              return "grey"
        hues   = hsv[:, :, 0][mask]
        mean_h = float(np.mean(hues))
        mean_s = float(np.mean(s[mask]))
        if mean_s < 30:
            mean_v = float(np.mean(v))
            if mean_v > 170:  return "white"
            elif mean_v < 70: return "black"
            return "grey"
        if mean_s < 80 and 10 <= mean_h <= 25:
            return "brown"
        for color_name, hue_min, hue_max in COLOR_RANGES:
            if hue_min <= mean_h <= hue_max:
                return color_name
        return "multi"
    except:
        return "multi"


# ── FIXED: Category → sleeve / occasion ──────────────────────────────────────
#
# SLEEVE_MAP rules:
#   "short"      → t-shirt (has sleeves but they're short)
#   "long"       → shirt (button-up, typically long), longsleeve, outwear
#   "sleeveless" → dress, skirt, pants, shorts, hat, shoes
#                  (these items either have no sleeves or are not tops)
#
# WHY THIS MATTERS: The sleeve filter in React does an exact string match.
# If a t-shirt is stored as "sleeveless", filtering "short" will never find it.
#
SLEEVE_MAP = {
    "t-shirt":   "short",       # ✅ FIXED: was missing, defaulted to wrong value
    "shirt":     "long",        # button-up shirts are typically long-sleeved
    "longsleeve":"long",        # explicitly long
    "outwear":   "long",        # jackets/coats are long
    "dress":     "sleeveless",  # dresses don't have arm sleeves as a category
    "skirt":     "sleeveless",  # bottom-wear
    "pants":     "sleeveless",  # bottom-wear
    "shorts":    "sleeveless",  # bottom-wear
    "hat":       "sleeveless",  # accessory
    "shoes":     "sleeveless",  # accessory
}

OCCASION_MAP = {
    "dress":      "party",
    "skirt":      "casual",
    "pants":      "formal",
    "shorts":     "casual",
    "shirt":      "formal",
    "t-shirt":    "casual",
    "longsleeve": "casual",
   
   
}


# ── Main processing ───────────────────────────────────────────────────────────
def process_images():
    outfits = []

    categories = [
        d for d in os.listdir(BASE_FOLDER)
        if os.path.isdir(os.path.join(BASE_FOLDER, d))
    ]
    print(f"\n📂 Categories found: {categories}\n")

    for category in categories:
        cat_path = os.path.join(BASE_FOLDER, category)
        files    = [
            f for f in os.listdir(cat_path)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ]
        print(f"📁 {category}: {len(files)} images")

        for i, file in enumerate(files):
            image_path = os.path.join(cat_path, file)
            print(f"   [{i+1}/{len(files)}] {file[:40]}", end=" ... ")

            features = extract_features(image_path)
            color    = detect_color_from_image(image_path)

            # Use SLEEVE_MAP with fallback to "short" for any unknown top categories
            cat_lower = category.lower().strip()
            sleeves  = SLEEVE_MAP.get(cat_lower, "short")
            occasion = OCCASION_MAP.get(cat_lower, "casual")

            print(f"color={color}, sleeves={sleeves}, features={len(features)} dims")

            outfits.append({
                "name":       file.split(".")[0],
                "category":   cat_lower,
                "image_path": f"{category}/{file}",
                "color":      color,
                "sleeves":    sleeves,
                "occasion":   occasion,
                "features":   features,
            })

    print(f"\n📊 Total: {len(outfits)} outfits processed")

    if not outfits:
        print("⚠️  No outfits found!")
        return

    print("\n🗑️  Clearing old MongoDB data...")
    collection.delete_many({})

    print("💾 Inserting into MongoDB in batches...")
    batch_size = 50
    for i in range(0, len(outfits), batch_size):
        batch = outfits[i:i + batch_size]
        collection.insert_many(batch)
        print(f"   ✅ Batch {i // batch_size + 1}: {len(batch)} outfits")

    from collections import Counter
    print(f"\n✅ Done! {len(outfits)} outfits inserted with feature vectors")
    print(f"   Colors:     {dict(Counter(o['color']    for o in outfits))}")
    print(f"   Occasions:  {dict(Counter(o['occasion'] for o in outfits))}")
    print(f"   Categories: {dict(Counter(o['category'] for o in outfits))}")
    print(f"   Sleeves:    {dict(Counter(o['sleeves']  for o in outfits))}")
    print(f"   Feature dim: {len(outfits[0]['features'])} per outfit")


if __name__ == "__main__":
    process_images()