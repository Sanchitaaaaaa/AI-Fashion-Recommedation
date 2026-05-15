import pandas as pd
import os
import shutil

CSV_PATH = "fashion_dataset/styles.csv"
IMAGES_PATH = "fashion_dataset/images"

df = pd.read_csv(CSV_PATH, on_bad_lines='skip')

for _, row in df.iterrows():

    try:
        image_id = str(row["id"]) + ".jpg"

        gender = str(row["gender"]).lower()
        article = str(row["articleType"]).lower()

        source = os.path.join(IMAGES_PATH, image_id)

        if not os.path.exists(source):
            continue

        # REMOVE KIDS
        if gender in ["boys", "girls", "unisex"]:
            continue

        # REMOVE SHOES
        shoe_keywords = [
            "shoe", "sandal", "heel",
            "flip flop", "slipper", "boot"
        ]

        if any(word in article for word in shoe_keywords):
            continue

        # ACCESSORIES
        accessory_keywords = [
            "watch", "bag", "belt",
            "cap", "wallet", "sunglass"
        ]

        if any(word in article for word in accessory_keywords):
            category = "accessories"

        elif gender == "men":

            if "shirt" in article:
                category = "mens_shirts"

            elif "jean" in article:
                category = "mens_jeans"

            else:
                category = "mens_tshirts"

        elif gender == "women":

            if "dress" in article:
                category = "womens_dresses"

            elif "kurta" in article:
                category = "womens_kurtis"

            elif "jean" in article:
                category = "womens_jeans"

            else:
                category = "womens_tops"

        else:
            continue

        destination_folder = os.path.join(IMAGES_PATH, category)

        os.makedirs(destination_folder, exist_ok=True)

        destination = os.path.join(destination_folder, image_id)

        shutil.move(source, destination)

    except Exception as e:
        print("Error:", e)

print("Dataset Organized Successfully!")