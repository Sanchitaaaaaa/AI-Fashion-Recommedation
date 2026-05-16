"""
generate_embeddings.py
======================
Run this ONCE to extract MobileNetV2 feature vectors for every outfit in MongoDB
and store them back as a 'features' field.

Usage:
    python generate_embeddings.py

Requirements:
    pip install tensorflow pillow pymongo python-dotenv numpy tqdm
"""

import os
import io
import json
import numpy as np
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient
from tqdm import tqdm

# ── TensorFlow / Keras ─────────────────────────────────────────────────────────
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing import image as keras_image
from tensorflow.keras.models import Model

# ── PIL ────────────────────────────────────────────────────────────────────────
from PIL import Image

# ==============================================================================
# CONFIG — adjust these paths to match your setup
# ==============================================================================

load_dotenv()

MONGO_URL        = os.getenv("MONGO_URL")
IMAGES_FOLDER    = os.getenv("IMAGES_FOLDER", "./fashion_images")   # local folder with images
BATCH_SIZE       = 64     # process this many images at once
IMG_SIZE         = (224, 224)

# ==============================================================================
# LOAD MODEL  (output = 1280-dim vector, no top classifier)
# ==============================================================================

print("⏳  Loading MobileNetV2 …")
base_model  = MobileNetV2(weights="imagenet", include_top=False, input_shape=(224, 224, 3))
# GlobalAveragePooling → 1280-d embedding
feature_extractor = Model(
    inputs  = base_model.input,
    outputs = tf.keras.layers.GlobalAveragePooling2D()(base_model.output)
)
feature_extractor.trainable = False
print("✅  Model loaded")

# ==============================================================================
# MONGO
# ==============================================================================

client     = MongoClient(MONGO_URL)
db         = client["ai_fashion"]
collection = db["outfits"]

# ==============================================================================
# HELPER: load & preprocess one image → numpy array (224,224,3)
# ==============================================================================

def load_image(path: str):
    try:
        img = Image.open(path).convert("RGB").resize(IMG_SIZE)
        arr = keras_image.img_to_array(img)
        arr = preprocess_input(arr)
        return arr
    except Exception as e:
        print(f"  ⚠️  Could not load {path}: {e}")
        return None


# ==============================================================================
# MAIN LOOP
# ==============================================================================

def generate_embeddings():

    # Only process outfits that don't have features yet (safe to re-run)
    outfits = list(collection.find({"features": {"$exists": False}}, {"_id": 1, "image_file": 1, "filename": 1}))
    print(f"\n📦  {len(outfits)} outfits need embeddings\n")

    if not outfits:
        print("✅  All outfits already have embeddings — nothing to do.")
        return

    processed  = 0
    skipped    = 0

    # Process in batches
    for i in tqdm(range(0, len(outfits), BATCH_SIZE), desc="Embedding batches"):

        batch       = outfits[i : i + BATCH_SIZE]
        batch_imgs  = []
        batch_ids   = []

        for doc in batch:
            filename   = doc.get("image_file") or doc.get("filename", "")
            image_path = os.path.join(IMAGES_FOLDER, filename)

            arr = load_image(image_path)
            if arr is None:
                skipped += 1
                continue

            batch_imgs.append(arr)
            batch_ids.append(doc["_id"])

        if not batch_imgs:
            continue

        # ── Extract features ──────────────────────────────────────────────────
        batch_tensor = np.array(batch_imgs, dtype=np.float32)          # (N,224,224,3)
        features     = feature_extractor.predict(batch_tensor, verbose=0)  # (N,1280)

        # ── Write back to MongoDB ─────────────────────────────────────────────
        for doc_id, feat_vec in zip(batch_ids, features):
            collection.update_one(
                {"_id": doc_id},
                {"$set": {"features": feat_vec.tolist()}}   # store as JSON array
            )
            processed += 1

    print(f"\n✅  Done!  Processed: {processed}  |  Skipped (bad image): {skipped}")
    client.close()


if __name__ == "__main__":
    generate_embeddings()