"""
verify_db.py
────────────
Run after bulk_insert_outfits.py to confirm the DB has clean data.
Prints breakdowns by gender, masterCategory, subCategory, articleType.

Usage:
    python verify_db.py
"""

import os
from collections import Counter
from pymongo import MongoClient
from dotenv import load_dotenv
import certifi

load_dotenv()

client     = MongoClient(os.getenv("MONGO_URL"), tlsCAFile=certifi.where())
db         = client["ai_fashion"]
collection = db["outfits"]

total = collection.count_documents({})
print(f"\n📦  Total outfits in DB : {total}\n")

docs = list(collection.find({}, {
    "_id": 0, "gender": 1, "master_category": 1,
    "subcategory": 1, "article_type": 1, "occasion": 1,
}))

def show_breakdown(label, key):
    print(f"── {label} ──────────────────────")
    for val, cnt in Counter(d.get(key, "?") for d in docs).most_common():
        print(f"   {val:<30} {cnt}")
    print()

show_breakdown("Gender",          "gender")
show_breakdown("Master Category", "master_category")
show_breakdown("Sub-Category",    "subcategory")
show_breakdown("Article Type",    "article_type")
show_breakdown("Occasion/Usage",  "occasion")

# Check for any forbidden values
print("── Sanity checks ──────────────────────────────")
forbidden_genders = [d for d in docs if d.get("gender") not in ("Men", "Women")]
forbidden_cats    = [d for d in docs if d.get("master_category") != "Apparel"]

print(f"  Docs with forbidden gender       : {len(forbidden_genders)}")
print(f"  Docs with non-Apparel category   : {len(forbidden_cats)}")

if forbidden_genders:
    print("  ⚠️  Sample forbidden genders:",
          list({d['gender'] for d in forbidden_genders})[:5])
if forbidden_cats:
    print("  ⚠️  Sample forbidden categories:",
          list({d['master_category'] for d in forbidden_cats})[:5])

if not forbidden_genders and not forbidden_cats:
    print("  ✅  All documents pass gender + category filters!")
print()