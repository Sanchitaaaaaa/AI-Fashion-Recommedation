#!/usr/bin/env python3
"""Add outfit images from nested folders to MongoDB with base64 encoding"""

from pymongo import MongoClient
import os
from dotenv import load_dotenv
import base64
from pathlib import Path

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")

if not MONGO_URL:
    print("❌ ERROR: MONGO_URL not set in .env")
    exit(1)

print("Connecting to MongoDB...")
client = MongoClient(MONGO_URL)
db = client["ai_fashion"]

# Path to outfit images folder
OUTFIT_IMAGES_PATH = "outfit_images"

def encode_image_to_base64(image_path):
    """Read image file and convert to base64"""
    try:
        with open(image_path, 'rb') as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
            return image_data
    except Exception as e:
        print(f"      Error reading image: {str(e)}")
        return None

def get_outfit_files_from_subfolders():
    """Get all image files from nested folders like dress/, hats/, etc."""
    if not os.path.exists(OUTFIT_IMAGES_PATH):
        print(f"❌ ERROR: {OUTFIT_IMAGES_PATH} folder not found!")
        return []
    
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    outfit_files = []
    
    # Get all subfolders (dress, hats, etc.)
    for subfolder in sorted(os.listdir(OUTFIT_IMAGES_PATH)):
        subfolder_path = os.path.join(OUTFIT_IMAGES_PATH, subfolder)
        
        # Skip if not a folder
        if not os.path.isdir(subfolder_path):
            continue
        
        print(f"📁 Found folder: {subfolder}/")
        
        # Get all images in this subfolder
        for file in sorted(os.listdir(subfolder_path)):
            file_path = os.path.join(subfolder_path, file)
            
            if os.path.isfile(file_path) and any(file.lower().endswith(ext) for ext in image_extensions):
                outfit_files.append({
                    'filename': file,
                    'filepath': file_path,
                    'category': subfolder,
                    'name': f"{subfolder.capitalize()} - {file.split('.')[0]}"
                })
    
    return outfit_files

try:
    # Get outfit images from nested folders
    outfit_files = get_outfit_files_from_subfolders()
    
    if not outfit_files:
        print(f"\n❌ No image files found in {OUTFIT_IMAGES_PATH}/ subfolders!")
        print("   Expected structure:")
        print("   outfit_images/")
        print("   ├── dress/")
        print("   │   ├── image1.jpg")
        print("   │   └── image2.jpg")
        print("   ├── hats/")
        print("   │   └── image1.jpg")
        print("   └── ...")
        exit(1)
    
    print(f"\n✅ Found {len(outfit_files)} total image files\n")
    
    outfits_collection = db["outfits"]
    
    # OPTION 1: Clear and recreate (uncomment if you want fresh data)
    # deleted = outfits_collection.delete_many({})
    # print(f"✅ Deleted {deleted.deleted_count} existing outfits\n")
    
    # OPTION 2: Update existing outfits with images (RECOMMENDED)
    print("Updating existing outfits with images...\n")
    
    inserted_count = 0
    updated_count = 0
    
    for outfit_info in outfit_files:
        outfit_name = outfit_info['filename']
        filepath = outfit_info['filepath']
        category = outfit_info['category']
        
        print(f"  {outfit_name}...", end="", flush=True)
        
        # Encode image to base64
        image_data = encode_image_to_base64(filepath)
        
        if image_data:
            # Try to UPDATE existing outfit first
            result = outfits_collection.update_one(
                {"name": outfit_name},
                {
                    "$set": {
                        "image": image_data,
                        "category": category,
                        "filename": outfit_info['filename']
                    }
                }
            )
            
            if result.matched_count > 0:
                updated_count += 1
                print(" ✅ (updated)")
            else:
                # If not found, insert new
                outfit = {
                    "name": outfit_name,
                    "type": category.lower(),
                    "color": "Multi",
                    "sleeves": "Short Sleeves",
                    "occasion": "Casual",
                    "image": image_data,
                    "filename": outfit_info['filename'],
                    "category": category,
                    "body_types": ["hourglass", "pear", "rectangle", "apple"],
                    "skin_tones": ["fair", "medium", "tan", "deep"],
                    "features": [0.0] * 512
                }
                
                outfits_collection.insert_one(outfit)
                inserted_count += 1
                print(" ✅ (inserted)")
        else:
            print(" ❌ (failed)")
    
    # Verify
    total = outfits_collection.count_documents({})
    with_images = outfits_collection.count_documents({"image": {"$ne": None}})
    
    print(f"\n{'='*60}")
    print(f"✅ COMPLETE!")
    print(f"{'='*60}")
    print(f"Total outfits in database: {total}")
    print(f"Outfits with images: {with_images}")
    print(f"Updated: {updated_count}")
    print(f"Inserted: {inserted_count}")
    
    # Show breakdown by category
    print(f"\n📊 Breakdown by category:")
    for category in set(item['category'] for item in outfit_files):
        cat_count = sum(1 for item in outfit_files if item['category'] == category)
        print(f"   {category.capitalize()}: {cat_count} images")
    
    print(f"\n{'='*60}")
    print(f"🎉 Real outfit images successfully added!")
    print(f"{'='*60}")

except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)