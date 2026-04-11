"""
Outfit Processor - Extracts REAL MobileNet feature vectors from images
These vectors capture visual style, texture, shape of each outfit.
Stored in MongoDB and used for real cosine similarity scoring.
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
    # MobileNetV2 pretrained on ImageNet - extracts 1280-dim feature vector
    base_model = tf.keras.applications.MobileNetV2(
        weights="imagenet",
        include_top=False,   # remove classification head
        pooling="avg",       # global average pooling → (1, 1280)
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
    """
    Extract 1280-dimensional feature vector using MobileNetV2.
    This vector encodes the visual appearance of the outfit.
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            return []

        # Resize to MobileNet input size
        img = cv2.resize(img, (224, 224))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Preprocess for MobileNetV2
        img = tf.keras.applications.mobilenet_v2.preprocess_input(img)
        img = np.expand_dims(img, axis=0)  # (1, 224, 224, 3)

        # Extract features
        features = base_model.predict(img, verbose=0)  # (1, 1280)
        features = features.flatten()                   # (1280,)

        # Normalize to unit vector (important for cosine similarity)
        norm = np.linalg.norm(features)
        if norm > 0:
            features = features / norm

        return features.tolist()

    except Exception as e:
        print(f"   ⚠️  Feature extraction error: {e}")
        return []


def extract_color_histogram_features(image_path: str) -> list:
    """
    Fallback: Extract color histogram as feature vector (96 dims).
    Less accurate than MobileNet but works without TensorFlow.
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            return []

        img = cv2.resize(img, (100, 100))
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # 32-bin histogram per channel = 96 total features
        h_hist = cv2.calcHist([hsv], [0], None, [32], [0, 180]).flatten()
        s_hist = cv2.calcHist([hsv], [1], None, [32], [0, 256]).flatten()
        v_hist = cv2.calcHist([hsv], [2], None, [32], [0, 256]).flatten()

        features = np.concatenate([h_hist, s_hist, v_hist])

        # Normalize
        norm = np.linalg.norm(features)
        if norm > 0:
            features = features / norm

        return features.tolist()

    except Exception as e:
        print(f"   ⚠️  Histogram error: {e}")
        return []


def extract_features(image_path: str) -> list:
    """Use MobileNet if available, else color histogram"""
    if USE_MOBILENET:
        return extract_mobilenet_features(image_path)
    return extract_color_histogram_features(image_path)


# ── Color detection from pixels ───────────────────────────────────────────────
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

        hues    = hsv[:, :, 0][mask]
        mean_h  = float(np.mean(hues))
        mean_s  = float(np.mean(s[mask]))

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


# ── Category → sleeve / occasion ─────────────────────────────────────────────
SLEEVE_MAP  = {
    "dress": "sleeveless", "t-shirt": "short", "shirt": "long",
    "longsleeve": "long",  "outwear": "long",  "pants": "sleeveless",
    "shorts": "sleeveless","skirt": "sleeveless","hat": "sleeveless","shoes": "sleeveless",
}
OCCASION_MAP = {
    "dress": "party",   "skirt": "casual",  "pants": "casual",
    "shorts": "casual", "shirt": "formal",  "t-shirt": "casual",
    "longsleeve": "casual","outwear": "casual","hat": "casual","shoes": "casual",
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

            # ── Extract feature vector (THE KEY STEP) ──────────────────────
            features = extract_features(image_path)

            # ── Detect attributes ───────────────────────────────────────────
            color    = detect_color_from_image(image_path)
            sleeves  = SLEEVE_MAP.get(category.lower(), "short")
            occasion = OCCASION_MAP.get(category.lower(), "casual")

            print(f"color={color}, features={len(features)} dims")

            outfits.append({
                "name":       file.split(".")[0],
                "category":   category.lower().strip(),
                "image_path": f"{category}/{file}",
                "color":      color,
                "sleeves":    sleeves,
                "occasion":   occasion,
                "features":   features,   # ← 1280-dim MobileNet vector
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
    print(f"   Feature dim: {len(outfits[0]['features'])} per outfit")


if __name__ == "__main__":
    process_images()