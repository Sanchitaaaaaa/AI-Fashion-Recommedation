import os
import numpy as np
from pymongo import MongoClient
from mobilenet import extract_outfit_features

MONGO_URI = "YOUR_MONGO_URI"

client = MongoClient(MONGO_URI)
db = client["fashion_ai"]
collection = db["outfits"]

BASE_FOLDER = "outfit_images"


def detect_color_from_filename(filename):
    filename = filename.lower()

    colors = ["red", "blue", "black", "white", "green", "yellow", "pink", "brown"]
    for color in colors:
        if color in filename:
            return color

    return "unknown"


def detect_sleeves_from_filename(filename):
    filename = filename.lower()

    if "long" in filename:
        return "long"
    elif "short" in filename:
        return "short"
    elif "sleeveless" in filename:
        return "sleeveless"
    return "unknown"


def detect_occasion(category):
    if category in ["dress"]:
        return "party"
    elif category in ["pants", "hat"]:
        return "casual"
    return "daily"


def process_images():
    outfits = []

    for category in os.listdir(BASE_FOLDER):
        category_path = os.path.join(BASE_FOLDER, category)

        if os.path.isdir(category_path):
            for file in os.listdir(category_path):

                if file.lower().endswith((".jpg", ".png", ".jpeg")):

                    image_path = os.path.join(category_path, file)

                    print("Processing:", image_path)

                    features = extract_outfit_features(image_path)

                    if features is None:
                        continue

                    outfit = {
                        "name": file.split('.')[0],
                        "category": category,
                        "image": f"{category}/{file}",
                        "color": detect_color_from_filename(file),
                        "sleeves": detect_sleeves_from_filename(file),
                        "occasion": detect_occasion(category),
                        "features": features
                    }

                    outfits.append(outfit)

    if outfits:
        collection.delete_many({})
        collection.insert_many(outfits)
        print(f"✅ Inserted {len(outfits)} outfits successfully!")


if __name__ == "__main__":
    process_images()
