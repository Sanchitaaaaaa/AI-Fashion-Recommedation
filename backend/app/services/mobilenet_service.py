"""
Outfit Processor - Detects color from IMAGE PIXELS
All categories supported: dress, longsleeve, outwear, pants, shirt, shorts, skirt, t-shirt, hat, shoes
"""

import os
import numpy as np
from pymongo import MongoClient
from dotenv import load_dotenv
import certifi
import cv2

load_dotenv()

MONGO_URI = os.getenv("MONGO_URL")

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000, tlsCAFile=certifi.where())
db     = client["ai_fashion"]
collection = db["outfits"]

BASE_FOLDER = "outfit_images"


# ── Sleeve map ───────────────────────────────────────────────────────────────
SLEEVE_MAP = {
    "dress":      "sleeveless",
    "t-shirt":    "short",
    "shirt":      "long",
    "longsleeve": "long",
    "outwear":    "long",
    "pants":      "sleeveless",
    "shorts":     "sleeveless",
    "skirt":      "sleeveless",
    "hat":        "sleeveless",
    "shoes":      "sleeveless",
}

# ── Occasion map ─────────────────────────────────────────────────────────────
OCCASION_MAP = {
    "dress":      "party",
    "skirt":      "casual",
    "pants":      "casual",
    "shorts":     "casual",
    "shirt":      "formal",
    "t-shirt":    "casual",
    "longsleeve": "casual",
    "outwear":    "casual",
    "hat":        "casual",
    "shoes":      "casual",
}


def detect_color_from_image(image_path: str) -> str:
    """
    Detect dominant clothing color using HSV analysis.
    Removes background by ignoring very light (white) pixels.
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            return "multi"

        img = cv2.resize(img, (150, 150))
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        h = hsv[:, :, 0]  # hue
        s = hsv[:, :, 1]  # saturation
        v = hsv[:, :, 2]  # brightness

        # Remove background: ignore very bright (white bg) and very dark pixels
        # Keep pixels: not too bright, not too dark, has some saturation
        foreground_mask = (v < 220) & (v > 30) & (s > 15)

        total_fg = np.sum(foreground_mask)
        if total_fg < 100:
            # Fallback: use full image
            foreground_mask = np.ones(h.shape, dtype=bool)

        fg_h = h[foreground_mask]
        fg_s = s[foreground_mask]
        fg_v = v[foreground_mask]

        mean_s = float(np.mean(fg_s))
        mean_v = float(np.mean(fg_v))

        # Achromatic colors (low saturation)
        if mean_s < 30:
            if mean_v > 170:
                return "white"
            elif mean_v < 70:
                return "black"
            else:
                return "grey"

        mean_h = float(np.mean(fg_h))

        # Brown/beige detection (warm, low-medium saturation)
        if mean_s < 80 and 10 <= mean_h <= 25:
            return "brown"

        # Hue to color mapping (OpenCV hue is 0-180)
        if mean_h < 8 or mean_h >= 165:
            return "red"
        elif mean_h < 18:
            # Could be orange or brown
            if mean_s > 100:
                return "yellow"   # vivid orange-yellow
            return "brown"
        elif mean_h < 35:
            return "yellow"
        elif mean_h < 85:
            return "green"
        elif mean_h < 130:
            return "blue"
        elif mean_h < 145:
            return "purple"
        elif mean_h < 165:
            # Pink range
            if mean_s > 60:
                return "pink"
            return "grey"
        else:
            return "red"

    except Exception as e:
        print(f"   ⚠️  Color error: {e}")
        return "multi"


def detect_sleeves(category: str) -> str:
    return SLEEVE_MAP.get(category.lower().strip(), "short")


def detect_occasion(category: str) -> str:
    return OCCASION_MAP.get(category.lower().strip(), "casual")


def process_images():
    outfits = []

    categories_found = [
        d for d in os.listdir(BASE_FOLDER)
        if os.path.isdir(os.path.join(BASE_FOLDER, d))
    ]
    print(f"📂 Found categories: {categories_found}")

    for category in categories_found:
        category_path = os.path.join(BASE_FOLDER, category)
        files = [
            f for f in os.listdir(category_path)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ]

        print(f"\n📁 {category}: {len(files)} images")

        for file in files:
            image_path = os.path.join(category_path, file)

            color    = detect_color_from_image(image_path)
            sleeves  = detect_sleeves(category)
            occasion = detect_occasion(category)

            print(f"   {file[:35]:35s} → color={color:8s} sleeves={sleeves:10s} occasion={occasion}")

            outfits.append({
                "name":       file.split(".")[0],
                "category":   category.lower().strip(),
                "image_path": f"{category}/{file}",
                "color":      color,
                "sleeves":    sleeves,
                "occasion":   occasion,
            })

    print(f"\n📊 Total: {len(outfits)} outfits")

    if not outfits:
        print("⚠️  No outfits found. Check BASE_FOLDER path.")
        return

    print("🗑️  Clearing old MongoDB data...")
    collection.delete_many({})

    print("💾 Inserting into MongoDB...")
    batch_size = 100
    for i in range(0, len(outfits), batch_size):
        batch = outfits[i:i + batch_size]
        collection.insert_many(batch)
        print(f"   ✅ Batch {i // batch_size + 1}: {len(batch)} inserted")

    # ── Summary ──────────────────────────────────────────────────────────────
    from collections import Counter
    color_counts    = Counter(o["color"]    for o in outfits)
    occasion_counts = Counter(o["occasion"] for o in outfits)
    cat_counts      = Counter(o["category"] for o in outfits)
    sleeve_counts   = Counter(o["sleeves"]  for o in outfits)

    print(f"\n✅ Done! Inserted {len(outfits)} outfits")
    print(f"\n📈 Color distribution:    {dict(color_counts)}")
    print(f"📈 Occasion distribution: {dict(occasion_counts)}")
    print(f"📈 Category distribution: {dict(cat_counts)}")
    print(f"📈 Sleeve distribution:   {dict(sleeve_counts)}")


if __name__ == "__main__":
    process_images()