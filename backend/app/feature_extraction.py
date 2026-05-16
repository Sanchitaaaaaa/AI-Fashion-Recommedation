# ============================================================
# FILE: backend/app/feature_extraction.py
# ============================================================

import os
import pickle
import numpy as np
import pandas as pd

from tqdm import tqdm

from tensorflow.keras.applications.mobilenet_v2 import (
    MobileNetV2,
    preprocess_input
)

from tensorflow.keras.preprocessing import image

from tensorflow.keras.models import Model
from tensorflow.keras.layers import GlobalAveragePooling2D

# ============================================================
# PATHS
# ============================================================

BASE_DIR = "fashion_dataset"

CSV_PATH = os.path.join(
    BASE_DIR,
    "filtered_styles.csv"
)

IMAGES_DIR = os.path.join(
    BASE_DIR,
    "filtered_images"
)

STORAGE_DIR = "storage"

FEATURES_FILE = os.path.join(
    STORAGE_DIR,
    "features.pkl"
)

METADATA_FILE = os.path.join(
    STORAGE_DIR,
    "metadata.pkl"
)

# ============================================================
# CREATE STORAGE
# ============================================================

os.makedirs(
    STORAGE_DIR,
    exist_ok=True
)

# ============================================================
# LOAD MODEL
# ============================================================

print("\nLoading MobileNetV2 model...")

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

print("✅ MobileNetV2 loaded")

# ============================================================
# LOAD CSV
# ============================================================

print("\nLoading filtered CSV...")

df = pd.read_csv(CSV_PATH)

print(f"Rows loaded : {len(df)}")

# ============================================================
# VALIDATE REQUIRED COLUMNS
# ============================================================

required_columns = [

    "id",
    "gender",
    "articleType",
    "baseColour",
    "usage",
    "image_file",
    "productDisplayName",
]

for col in required_columns:

    if col not in df.columns:

        raise Exception(
            f"❌ Missing column: {col}"
        )

# ============================================================
# FEATURE EXTRACTION FUNCTION
# ============================================================

def extract_features(img_path):

    try:

        img = image.load_img(

            img_path,

            target_size=(224, 224)
        )

        img_array = image.img_to_array(img)

        img_array = np.expand_dims(
            img_array,
            axis=0
        )

        img_array = preprocess_input(
            img_array
        )

        features = model.predict(
            img_array,
            verbose=0
        )[0]

        # ====================================================
        # NORMALIZE VECTOR
        # ====================================================

        features = features / np.linalg.norm(
            features
        )

        return features

    except Exception as e:

        print(
            f"❌ Error extracting features "
            f"from {img_path}: {e}"
        )

        return None

# ============================================================
# LISTS
# ============================================================

all_features = []

all_metadata = []

# ============================================================
# PROCESS DATASET
# ============================================================

print("\nExtracting features...\n")

for _, row in tqdm(

    df.iterrows(),

    total=len(df)
):

    try:

        image_file = row["image_file"]

        image_path = os.path.join(
            IMAGES_DIR,
            image_file
        )

        # ====================================================
        # CHECK FILE EXISTS
        # ====================================================

        if not os.path.exists(image_path):

            continue

        # ====================================================
        # EXTRACT EMBEDDING
        # ====================================================

        embedding = extract_features(
            image_path
        )

        if embedding is None:
            continue

        # ====================================================
        # SAVE FEATURES
        # ====================================================

        all_features.append(
            embedding
        )

        # ====================================================
        # METADATA
        # ====================================================

        metadata = {

            "id":

                str(row["id"]),

            "image_file":

                image_file,

            "productDisplayName":

                row["productDisplayName"],

            "gender":

                row["gender"],

            "articleType":

                row["articleType"],

            "baseColour":

                row["baseColour"],

            "usage":

                row["usage"],

            "embedding":

                embedding.tolist(),

            # ================================================
            # OPTIONAL RECOMMENDATION TAGS
            # ================================================

            "recommended_body_type": [

                "Rectangle",
                "Pear",
                "Hourglass",
            ],

            "recommended_skin_tone": [

                "Fair",
                "Light Medium",
                "Medium",
            ],
        }

        all_metadata.append(
            metadata
        )

    except Exception as e:

        print(
            f"❌ Error processing row: {e}"
        )

        continue

# ============================================================
# SAVE FEATURES
# ============================================================

print("\nSaving features...")

with open(
    FEATURES_FILE,
    "wb"
) as f:

    pickle.dump(
        all_features,
        f
    )

# ============================================================
# SAVE METADATA
# ============================================================

print("Saving metadata...")

with open(
    METADATA_FILE,
    "wb"
) as f:

    pickle.dump(
        all_metadata,
        f
    )

# ============================================================
# DONE
# ============================================================

print("\n===================================")
print("✅ FEATURE EXTRACTION COMPLETE")
print("===================================")

print(
    f"Total embeddings : "
    f"{len(all_features)}"
)

print(
    f"Features saved -> "
    f"{FEATURES_FILE}"
)

print(
    f"Metadata saved -> "
    f"{METADATA_FILE}"
)