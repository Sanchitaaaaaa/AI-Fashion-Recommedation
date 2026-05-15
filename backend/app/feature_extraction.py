# =========================================================
# FILE: app/feature_extraction.py
# =========================================================

import os
import pickle
import numpy as np
import pandas as pd
import cv2

from tqdm import tqdm

from tensorflow.keras.applications.mobilenet_v2 import (

    MobileNetV2,
    preprocess_input
)

from tensorflow.keras.preprocessing.image import img_to_array

from tensorflow.keras.models import Model

from tensorflow.keras.layers import GlobalAveragePooling2D

# =========================================================
# PATHS
# =========================================================

DATASET_PATH = "fashion_dataset"

FILTERED_IMAGES = os.path.join(
    DATASET_PATH,
    "filtered_images"
)

FILTERED_CSV = os.path.join(
    DATASET_PATH,
    "filtered_styles.csv"
)

OUTPUT_PATH = "storage"

FEATURES_FILE = os.path.join(
    OUTPUT_PATH,
    "image_features.pkl"
)

METADATA_FILE = os.path.join(
    OUTPUT_PATH,
    "metadata.pkl"
)

os.makedirs(
    OUTPUT_PATH,
    exist_ok=True
)

# =========================================================
# IMAGE SETTINGS
# =========================================================

IMAGE_SIZE = (224, 224)

# =========================================================
# LOAD MODEL
# =========================================================

print("Loading MobileNetV2 model...")

base_model = MobileNetV2(

    weights="imagenet",

    include_top=False,

    input_shape=(224, 224, 3)
)

model = Model(

    inputs=base_model.input,

    outputs=GlobalAveragePooling2D()(
        base_model.output
    )
)

print("✅ Model loaded")

# =========================================================
# LOAD CSV
# =========================================================

print("\nLoading filtered CSV...")

df = pd.read_csv(
    FILTERED_CSV
)

print(f"Total rows : {len(df)}")

# =========================================================
# VALID IMAGE FILES
# =========================================================

image_files = [

    f for f in os.listdir(
        FILTERED_IMAGES
    )

    if f.lower().endswith(

        (
            ".jpg",
            ".jpeg",
            ".png",
            ".webp"
        )
    )
]

print(f"Valid image files : {len(image_files)}")

# =========================================================
# FEATURE EXTRACTION
# =========================================================

features = []

metadata = []

# =========================================================
# IMAGE PREPROCESS
# =========================================================

def preprocess_image(image_path):

    try:

        image = cv2.imread(image_path)

        if image is None:
            return None

        image = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB
        )

        image = cv2.resize(
            image,
            IMAGE_SIZE
        )

        image = img_to_array(image)

        image = np.expand_dims(
            image,
            axis=0
        )

        image = preprocess_input(
            image
        )

        return image

    except Exception as e:

        print(
            f"❌ Preprocess error: {e}"
        )

        return None

# =========================================================
# EXTRACT LOOP
# =========================================================

print("\nExtracting features...\n")

for image_file in tqdm(image_files):

    try:

        image_path = os.path.join(
            FILTERED_IMAGES,
            image_file
        )

        processed = preprocess_image(
            image_path
        )

        if processed is None:
            continue

        # =================================================
        # FEATURE VECTOR
        # =================================================

        embedding = model.predict(
            processed,
            verbose=0
        )[0]

        embedding = embedding / np.linalg.norm(
            embedding
        )

        features.append(
            embedding
        )

        # =================================================
        # IMAGE ID
        # =================================================

        image_id = os.path.splitext(
            image_file
        )[0]

        # =================================================
        # CSV MATCH
        # =================================================

        row = df[
            df["id"].astype(str)
            == str(image_id)
        ]

        if len(row) == 0:
            continue

        row = row.iloc[0]

        metadata.append({

            "id": str(image_id),

            "image_file": image_file,

            "gender": str(
                row.get("gender", "")
            ),

            "masterCategory": str(
                row.get("masterCategory", "")
            ),

            "subCategory": str(
                row.get("subCategory", "")
            ),

            "articleType": str(
                row.get("articleType", "")
            ),

            "baseColour": str(
                row.get("baseColour", "")
            ),

            "season": str(
                row.get("season", "")
            ),

            "usage": str(
                row.get("usage", "")
            ),
        })

    except Exception as e:

        print(
            f"❌ Feature extraction failed: {e}"
        )

# =========================================================
# CONVERT TO NUMPY
# =========================================================

features = np.array(
    features
)

print("\n========== SUMMARY ==========")

print(f"Feature vectors : {len(features)}")

print(f"Metadata rows   : {len(metadata)}")

# =========================================================
# SAVE FEATURES
# =========================================================

with open(
    FEATURES_FILE,
    "wb"
) as f:

    pickle.dump(
        features,
        f
    )

print(
    f"\n✅ Features saved -> {FEATURES_FILE}"
)

# =========================================================
# SAVE METADATA
# =========================================================

with open(
    METADATA_FILE,
    "wb"
) as f:

    pickle.dump(
        metadata,
        f
    )

print(
    f"✅ Metadata saved -> {METADATA_FILE}"
)

print("\n🎉 Feature extraction completed!")