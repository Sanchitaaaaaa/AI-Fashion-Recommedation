"""
patch_sleeve_values.py
──────────────────────
Run ONCE after bulk_insert_outfits.py to:
  1. Fix/confirm sleeve values in MongoDB.
  2. Populate / fix display_category for any docs missing it.

Usage:
    python patch_sleeve_values.py
"""

import os
from collections import Counter
from pymongo import MongoClient
from dotenv import load_dotenv
import certifi

load_dotenv()

MONGO_URI  = os.getenv("MONGO_URL")
client     = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=10000,
    tlsCAFile=certifi.where(),
)
db         = client["ai_fashion"]
collection = db["outfits"]

# ============================================================
# SLEEVE MAP  (articleType → sleeve)
# ============================================================

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
    "Dupatta":        "sleeveless",
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
# DISPLAY CATEGORY MAPS
# ============================================================

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

# ============================================================
# PATCH 1 — SLEEVE VALUES
# ============================================================

print("🔧  Patching sleeve values …\n")
total_sleeves = 0

for article_type, sleeve_value in SLEEVE_MAP.items():
    result = collection.update_many(
        {"category": article_type},
        {"$set": {"sleeves": sleeve_value}},
    )
    if result.modified_count > 0:
        print(f"   ✅  {article_type:<25} → '{sleeve_value}'  "
              f"({result.modified_count} docs)")
    total_sleeves += result.modified_count

print(f"\n✅  Sleeve patch done. Total updated: {total_sleeves}")

# ============================================================
# PATCH 2 — DISPLAY CATEGORY  (Men)
# ============================================================

print("\n🔧  Patching display_category for Men …\n")
total_display = 0

for article_type, disp_cat in MEN_DISPLAY_CATEGORY.items():
    result = collection.update_many(
        {"gender": "Men", "category": article_type},
        {"$set": {"display_category": disp_cat}},
    )
    if result.modified_count > 0:
        print(f"   ✅  Men | {article_type:<25} → '{disp_cat}'  "
              f"({result.modified_count} docs)")
    total_display += result.modified_count

# ============================================================
# PATCH 3 — DISPLAY CATEGORY  (Women)
# ============================================================

print("\n🔧  Patching display_category for Women …\n")

for article_type, disp_cat in WOMEN_DISPLAY_CATEGORY.items():
    result = collection.update_many(
        {"gender": "Women", "category": article_type},
        {"$set": {"display_category": disp_cat}},
    )
    if result.modified_count > 0:
        print(f"   ✅  Women | {article_type:<25} → '{disp_cat}'  "
              f"({result.modified_count} docs)")
    total_display += result.modified_count

print(f"\n✅  Display category patch done. Total updated: {total_display}")

# ============================================================
# VERIFY
# ============================================================

print("\n📊  Distribution after patch:\n")
all_docs = list(collection.find(
    {}, {"_id": 0, "gender": 1, "category": 1,
          "sleeves": 1, "display_category": 1}
))

print("── Sleeve counts ──────────────────────────────")
sleeve_cnt = Counter(d.get("sleeves", "unset") for d in all_docs)
for s, n in sorted(sleeve_cnt.items()):
    print(f"   {s:<14} {n}")

print("\n── Display category counts (Men) ──────────────")
men_cnt = Counter(
    d.get("display_category", "?")
    for d in all_docs if d.get("gender") == "Men"
)
for cat, n in sorted(men_cnt.items()):
    print(f"   {cat:<20} {n}")

print("\n── Display category counts (Women) ─────────────")
women_cnt = Counter(
    d.get("display_category", "?")
    for d in all_docs if d.get("gender") == "Women"
)
for cat, n in sorted(women_cnt.items()):
    print(f"   {cat:<20} {n}")

print()