# ============================================================
# FILE: backend/app/dataset_filter.py
# ============================================================

"""
Filters raw Myntra styles.csv
→ fashion_dataset/filtered_styles.csv

Copies matching images
→ fashion_dataset/filtered_images/

ALLOWED:
- Men/Women only
- Apparel only
- Fashion clothing only

BLOCKED:
- Kids
- Boys
- Girls
- Innerwear
- Shoes
- Accessories
- Beauty products
"""

import os
import shutil
import pandas as pd

# ============================================================
# PATHS
# ============================================================

DATASET_PATH = "fashion_dataset"

IMAGES_PATH = os.path.join(
    DATASET_PATH,
    "images"
)

CSV_PATH = os.path.join(
    DATASET_PATH,
    "styles.csv"
)

FILTERED_IMAGES = os.path.join(
    DATASET_PATH,
    "filtered_images"
)

FILTERED_CSV = os.path.join(
    DATASET_PATH,
    "filtered_styles.csv"
)

# ============================================================
# CREATE OUTPUT FOLDER
# ============================================================

os.makedirs(
    FILTERED_IMAGES,
    exist_ok=True
)

# ============================================================
# FILTER SETTINGS
# ============================================================

ALLOWED_GENDER = {

    "Men",
    "Women"
}

ALLOWED_MASTER_CATEGORY = {

    "Apparel"
}

ALLOWED_USAGE = {

    "Casual",
    "Party",
    "Sports",
    "Ethnic",
    "Formal",
}

# ============================================================
# MEN CATEGORIES
# ============================================================

MEN_ALLOWED_ARTICLES = {

    "Tshirts",
    "Shirts",

    "Kurtas",
    "Kurta Sets",

    "Sweatshirts",
    "Hoodies",

    "Jeans",
    "Trousers",
    "Shorts",
    "Track Pants",
    "Joggers",
    "Cargos",

    "Blazers",
    "Suits",
    "Waistcoat",

    "Jackets",
    "Windcheater",
}

# ============================================================
# WOMEN CATEGORIES
# ============================================================

WOMEN_ALLOWED_ARTICLES = {

    "Tshirts",
    "Shirts",
    "Tops",
    "Blouses",
    "Tunics",

    "Kurtas",
    "Kurtis",
    "Kurta Sets",

    "Suits",
    "Suit Sets",

    "Jeans",
    "Trousers",
    "Shorts",
    "Skirts",
    "Leggings",
    "Track Pants",
    "Joggers",
    "Cargos",

    "Dresses",
    "Jumpsuits",

    "Jackets",
    "Blazers",
    "Sweatshirts",
    "Hoodies",
}

# ============================================================
# HARD EXCLUSIONS
# ============================================================

HARD_EXCLUDED = {

    # Footwear
    "Shoes",
    "Casual Shoes",
    "Sports Shoes",
    "Formal Shoes",
    "Heels",
    "Flats",
    "Sandals",
    "Flip Flops",
    "Boots",

    # Bags
    "Bags",
    "Handbags",
    "Wallets",
    "Backpacks",

    # Accessories
    "Belts",
    "Watches",
    "Jewellery",
    "Sunglasses",
    "Caps",
    "Hat",

    # Hosiery
    "Socks",
    "Stockings",

    # Innerwear
    "Bra",
    "Briefs",
    "Boxers",
    "Trunk",
    "Innerwear Vests",
    "Camisoles",
    "Shapewear",
    "Lingerie Set",
    "Swimwear",
    "Bikini",
    "Rompers",
    "Trunk",
    "Trunks",
    "Innerwear Vests",
    "Baby Dolls",
    "Swimwear",

    # Beauty
    "Perfume and Body Mist",
    "Lipstick",
    "Nail Polish",
    "Compact",

    # Misc
    "Water Bottle",
    "Umbrellas",
}

# ============================================================
# LOAD CSV
# ============================================================

print("\nLoading styles.csv ...")

df = pd.read_csv(
    CSV_PATH,
    on_bad_lines="skip"
)

print(
    f"Total rows : {len(df)}"
)

# ============================================================
# USAGE FILTER
# ============================================================

df = df[
    df["usage"].isin(
        ALLOWED_USAGE
    )
]

print(
    f"After usage filter : {len(df)}"
)

# ============================================================
# GENDER FILTER
# ============================================================

df = df[
    df["gender"].isin(
        ALLOWED_GENDER
    )
]

print(
    f"After gender filter : {len(df)}"
)

# ============================================================
# REMOVE KIDS PRODUCTS
# ============================================================
# ============================================================
# REMOVE KIDS / INNERWEAR PRODUCTS
# ============================================================

blocked_words = [

    # kids

    "kids",
    "girls",
    "boys",
    "baby",
    "infant",
    "toddler",
    "junior",

    # innerwear

    "romper",
    "trunk",
    "brief",
    "boxer",
    "bra",
    "lingerie",
    "camisole",
    "nightdress",
    "night suit",
    "innerwear",

    # brands often kids

    "gini and jony",
]

df = df[

    ~df["productDisplayName"]

    .astype(str)

    .str.lower()

    .str.contains(

        "|".join(blocked_words),

        na=False
    )
]

# ============================================================
# APPAREL ONLY
# ============================================================

df = df[
    df["masterCategory"].isin(
        ALLOWED_MASTER_CATEGORY
    )
]

print(
    f"After apparel filter : {len(df)}"
)

# ============================================================
# REMOVE BAD CATEGORIES
# ============================================================

df = df[
    ~df["articleType"]
    .isin(HARD_EXCLUDED)
]

print(
    f"After exclusions : {len(df)}"
)

# ============================================================
# MEN/WOMEN ARTICLE FILTER
# ============================================================

def is_allowed(row):

    gender = row["gender"]

    article = row["articleType"]

    if gender == "Men":

        return article in MEN_ALLOWED_ARTICLES

    elif gender == "Women":

        return article in WOMEN_ALLOWED_ARTICLES

    return False

df = df[
    df.apply(
        is_allowed,
        axis=1
    )
].copy()

print(
    f"After article filter : {len(df)}"
)

# ============================================================
# CLEAN IDS
# ============================================================

df = df.dropna(
    subset=["id"]
)

df["id"] = df["id"].astype(int)

# ============================================================
# VALIDATE IMAGES
# ============================================================

print("\nValidating images ...")

valid_rows = []

for _, row in df.iterrows():

    image_id = str(row["id"])

    possible_files = [

        f"{image_id}.jpg",
        f"{image_id}.jpeg",
        f"{image_id}.png",
        f"{image_id}.JPG",
    ]

    found = False

    for file_name in possible_files:

        image_path = os.path.join(
            IMAGES_PATH,
            file_name
        )

        if os.path.exists(image_path):

            # ================================================
            # SAVE IMAGE FILE NAME
            # ================================================

            row["image_file"] = file_name

            valid_rows.append(row)

            found = True

            break

    if not found:
        continue

# ============================================================
# NEW DATAFRAME
# ============================================================

df = pd.DataFrame(valid_rows)

print(
    f"Valid images : {len(df)}"
)

# ============================================================
# EMPTY CHECK
# ============================================================

if len(df) == 0:

    raise Exception(
        "\n❌ ZERO VALID IMAGES FOUND"
    )

# ============================================================
# BALANCE DATASET
# ============================================================

PER_GENDER = 1500

men_df = df[
    df["gender"] == "Men"
].head(PER_GENDER)

women_df = df[
    df["gender"] == "Women"
].head(PER_GENDER)

df = pd.concat([

    men_df,
    women_df

]).reset_index(drop=True)

print(
    f"\nFinal dataset : {len(df)}"
)

print(
    f"Men   : {len(men_df)}"
)

print(
    f"Women : {len(women_df)}"
)

# ============================================================
# COPY IMAGES
# ============================================================

print("\nCopying images ...")

copied = 0

for _, row in df.iterrows():

    file_name = row["image_file"]

    source = os.path.join(
        IMAGES_PATH,
        file_name
    )

    destination = os.path.join(
        FILTERED_IMAGES,
        file_name
    )

    if (

        os.path.exists(source)

        and

        not os.path.exists(destination)
    ):

        shutil.copy2(
            source,
            destination
        )

        copied += 1

print(
    f"Images copied : {copied}"
)

# ============================================================
# SAVE CSV
# ============================================================

df.to_csv(
    FILTERED_CSV,
    index=False
)

print(
    f"\nCSV saved -> {FILTERED_CSV}"
)

# ============================================================
# DONE
# ============================================================

print("\n" + "=" * 60)

print("✅ DATASET FILTER COMPLETE")

print("=" * 60)

print(
    f"Final rows : {len(df)}"
)

print(
    f"Filtered images : "
    f"{FILTERED_IMAGES}"
)

print("=" * 60)

# ============================================================
# ARTICLE BREAKDOWN
# ============================================================

print("\nTop article types:\n")

for article, count in (

    df["articleType"]

    .value_counts()

    .head(30)

    .items()
):

    print(f"{article:<25} {count}")