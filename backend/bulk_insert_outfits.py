import os
import cv2
import numpy as np
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URL")
if not MONGO_URI:
    print("❌ MONGO_URL not set")
    exit(1)

print("Connecting to MongoDB...")
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=30000, connectTimeoutMS=30000)
db = client["ai_fashion"]
collection = db["outfits"]

print("✅ MongoDB Connected\n")

DATASET_PATH = "outfit_images"

def get_body_types(cat):
    cat = cat.lower()
    if "dress" in cat:
        return ["hourglass", "pear", "rectangle", "apple"]
    elif "pants" in cat:
        return ["rectangle", "apple", "pear"]
    elif "longsleeve" in cat or "shirt" in cat or "t-shirt" in cat:
        return ["hourglass", "pear", "apple", "rectangle"]
    elif "outwear" in cat or "hat" in cat:
        return ["hourglass", "pear", "rectangle", "apple"]
    elif "shorts" in cat or "skirt" in cat:
        return ["hourglass", "pear", "apple"]
    else:
        return ["hourglass", "pear", "rectangle", "apple"]

def get_skin_tones(color):
    return ["fair", "medium", "tan", "deep"]

def get_occasion(cat):
    cat = cat.lower()
    if "dress" in cat:
        return "party"
    elif "outwear" in cat:
        return "casual"
    elif "shoe" in cat or "hat" in cat:
        return "casual"
    else:
        return "casual"

# Clear existing
print("Clearing existing outfits...")
result = collection.delete_many({})
print(f"Deleted {result.deleted_count} existing outfits\n")

total = 0
failed = 0
skipped = 0

for category in sorted(os.listdir(DATASET_PATH)):
    cat_path = os.path.join(DATASET_PATH, category)
    if not os.path.isdir(cat_path):
        continue
    
    images = [f for f in os.listdir(cat_path) 
              if f.lower().endswith(('.jpg', '.png', '.jpeg', '.webp'))]
    
    print(f"📁 Processing: {category}/ ({len(images)} images)")
    
    inserted = 0
    
    for img in images:
        img_path = os.path.join(cat_path, img)
        
        try:
            # Verify image can be read
            img_data = cv2.imread(img_path)
            if img_data is None:
                skipped += 1
                continue
            
            # Create document
            doc = {
                "name": img,
                "category": category,
                "color": "multi",
                "sleeves": "unknown",
                "occasion": get_occasion(category),
                "body_types": get_body_types(category),
                "skin_tones": get_skin_tones("multi"),
                "features": np.random.random(512).tolist()
            }
            
            # Insert
            collection.insert_one(doc)
            total += 1
            inserted += 1
            
            # Progress
            if inserted % 50 == 0:
                print(f"   ✅ Inserted {inserted}...")
        
        except Exception as e:
            print(f"   ❌ Error inserting {img}: {str(e)}")
            failed += 1
    
    print(f"   ✅ {category} complete: {inserted} inserted\n")

print("="*60)
print("✅ BULK INSERT COMPLETE")
print("="*60)
print(f"Total inserted: {total}")
print(f"Total failed: {failed}")
print(f"Total skipped: {skipped}")

# Verify
count = collection.count_documents({})
print(f"Total in database: {count}")

# Sample
sample = collection.find_one({})
if sample:
    print(f"\n📝 Sample outfit:")
    print(f"   Name: {sample.get('name')}")
    print(f"   Category: {sample.get('category')}")
    print(f"   Body types: {sample.get('body_types')}")
    print(f"   Occasion: {sample.get('occasion')}")

print("="*60)