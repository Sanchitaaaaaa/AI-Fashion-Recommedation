"""
patch_sleeve_values.py
─────────────────────
Run this ONCE to fix sleeve values in your existing MongoDB data.
This is much faster than re-running mobilenet_service.py (no image processing).

Usage:
    python patch_sleeve_values.py

What it fixes:
  - t-shirt  → "short"      (was getting wrong value from default)
  - shirt    → "long"
  - longsleeve → "long"
  - outwear  → "long"
  - dress/skirt/pants/shorts/hat/shoes → "sleeveless"
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv
import certifi

load_dotenv()

MONGO_URI  = os.getenv("MONGO_URL")
client     = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000, tlsCAFile=certifi.where())
db         = client["ai_fashion"]
collection = db["outfits"]

# Correct mapping: category → sleeve value
SLEEVE_MAP = {
    "t-shirt":    "short",
    "shirt":      "long",
    "longsleeve": "long",
    "outwear":    "long",
    "dress":      "sleeveless",
    "skirt":      "sleeveless",
    "pants":      "sleeveless",
    "shorts":     "sleeveless",
    "hat":        "sleeveless",
    "shoes":      "sleeveless",
}

print("🔧 Patching sleeve values in MongoDB...\n")

total_updated = 0

for category, correct_sleeve in SLEEVE_MAP.items():
    result = collection.update_many(
        {"category": category},
        {"$set": {"sleeves": correct_sleeve}}
    )
    if result.modified_count > 0:
        print(f"   ✅ {category:12} → sleeves='{correct_sleeve}'  ({result.modified_count} docs updated)")
    else:
        print(f"   ⚪ {category:12} → no docs found (0 updated)")
    total_updated += result.modified_count

print(f"\n✅ Done! Total documents updated: {total_updated}")

# Verify
print("\n📊 Sleeve distribution after patch:")
from collections import Counter
all_docs = list(collection.find({}, {"_id": 0, "category": 1, "sleeves": 1}))
for cat, sleeve in sorted(Counter((d["category"], d["sleeves"]) for d in all_docs).items()):
    print(f"   {cat[0]:12} → {cat[1]}")