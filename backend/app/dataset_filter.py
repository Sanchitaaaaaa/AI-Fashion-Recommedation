"""
dataset_filter.py
─────────────────
Filters raw Myntra styles.csv → fashion_dataset/filtered_styles.csv
and copies matching images → fashion_dataset/filtered_images/

Allowed article types
──────────────────────
MEN   : Tshirts · Shirts · Kurtas · Sweatshirts/Hoodies · Jeans ·
        Trousers · Shorts · Track Pants · Blazers · Jackets · Suits
WOMEN : Shirts · Tshirts · Tops · Kurtas/Kurtis · Suit Sets · Jeans ·
        Trousers · Shorts · Skirts · Track Pants · Dresses ·
        Jumpsuits · Blouses · Jackets · Sweatshirts
NEVER : Innerwear · Swimwear · Lingerie · Bra · Briefs ·
        Footwear · Bags · Jewellery · Socks · Personal care
"""

import os
import shutil
import cv2
import pandas as pd

# ============================================================
# PATHS
# ============================================================

DATASET_PATH    = "fashion_dataset"
IMAGES_PATH     = os.path.join(DATASET_PATH, "images")
CSV_PATH        = os.path.join(DATASET_PATH, "styles.csv")
FILTERED_IMAGES = os.path.join(DATASET_PATH, "filtered_images")
FILTERED_CSV    = os.path.join(DATASET_PATH, "filtered_styles.csv")

os.makedirs(FILTERED_IMAGES, exist_ok=True)

# ============================================================
# TOP-LEVEL FILTERS
# ============================================================

ALLOWED_GENDER     = {"Men", "Women"}
ALLOWED_MASTER_CAT = {"Apparel"}
ALLOWED_USAGE      = {"Casual", "Party", "Sports", "Ethnic", "Formal"}

# ============================================================
# MEN — allowed article types  (exact Myntra strings)
# ============================================================

MEN_ALLOWED_ARTICLES = {
    # T-shirts
    "Tshirts",
    # Shirts
    "Shirts",
    # Kurtas / ethnic
    "Kurtas", "Kurta Sets",
    # Hoodies / Sweatshirts
    "Sweatshirts", "Hoodies",
    # Bottoms
    "Jeans", "Trousers", "Shorts", "Cargos", "Joggers",
    # Gymwear
    "Track Pants", "Tracksuits", "Sports Jersey",
    # Blazers / Formal
    "Blazers", "Suits", "Suit Sets", "Nehru Jackets", "Waistcoat",
    # Jackets / Outerwear
    "Jackets", "Windcheater", "Rain Jacket",
}

# ============================================================
# WOMEN — allowed article types  (exact Myntra strings)
# ============================================================

WOMEN_ALLOWED_ARTICLES = {
    # Shirts / Tshirts / Tops
    "Shirts", "Tshirts", "Tops", "Blouses", "Tunics",
    # Kurtas / ethnic
    "Kurtas", "Kurtis", "Kurta Sets",
    "Salwar", "Churidar", "Sarees", "Lehenga Choli", "Dupatta",
    # Suit sets
    "Suits", "Suit Sets",
    # Bottoms
    "Jeans", "Trousers", "Shorts", "Skirts",
    "Capris", "Leggings", "Cargos", "Joggers",
    # Gymwear
    "Track Pants", "Tracksuits", "Sports Jersey",
    # Dresses / Jumpsuits
    "Dresses", "Jumpsuits", "Dungarees", "Co-ords",
    # Outerwear
    "Jackets", "Blazers", "Sweatshirts", "Hoodies",
    "Shrugs", "Windcheater", "Rain Jacket",
    # Tasteful nightwear (full coverage only)
    "Lounge Pants", "Lounge Shorts", "Lounge Tshirts", "Nightdress",
}

# ============================================================
# HARD EXCLUSION — blocked regardless of sub-category
# ============================================================

HARD_EXCLUDED = {
    # Footwear
    "Shoes", "Casual Shoes", "Sports Shoes", "Formal Shoes",
    "Heels", "Flats", "Sandals", "Flip Flops", "Boots", "Shoe Accessories",
    # Bags
    "Bags", "Handbags", "Wallets", "Clutches", "Backpacks",
    "Trolley Bag", "Messenger Bag", "Laptop Bag", "Travel Accessory",
    # Accessories
    "Belts", "Watches", "Jewellery", "Earrings", "Necklace", "Ring",
    "Bracelet", "Pendant", "Brooch", "Anklet",
    "Headwear", "Caps", "Hat", "Sunglasses", "Eyewear",
    # Hosiery
    "Socks", "Stockings", "Tights",
    # Innerwear / Swimwear / Lingerie — complete block
    "Bra", "Briefs", "Boxers", "Trunk",
    "Innerwear Vests", "Camisoles", "Shapewear",
    "Swimwear", "Bikini", "Swimsuit", "Board Shorts",
    "Bikini Top", "Bikini Bottom", "Lingerie Set",
    "Negligee", "Robe", "Baby Doll", "Suspenders",
    "Thermal Bottoms", "Thermal Tops",
    # Beauty / Personal care
    "Perfume and Body Mist", "Sunscreen", "Lipstick",
    "Nail Polish", "Foundation", "Mascara", "Compact",
    "Kajal and Eyeliner", "Lip Gloss", "Face Moisturisers",
    # Misc
    "Water Bottle", "Umbrellas", "Key chain",
    "Free Gifts", "Sports Accessories", "Vouchers",
}

# ============================================================
# LOAD
# ============================================================

print("Loading styles.csv …")
df = pd.read_csv(CSV_PATH, on_bad_lines="skip")
print(f"  Total rows            : {len(df)}")

df = df[df["usage"].isin(ALLOWED_USAGE)]
print(f"  After usage           : {len(df)}")

df = df[df["gender"].isin(ALLOWED_GENDER)]
print(f"  After gender          : {len(df)}")

df = df[df["masterCategory"].isin(ALLOWED_MASTER_CAT)]
print(f"  After masterCat       : {len(df)}")

df = df[~df["articleType"].isin(HARD_EXCLUDED)]
print(f"  After hard exclusions : {len(df)}")

# Per-gender article allow-list
def _allowed(row):
    if row["gender"] == "Men":
        return row["articleType"] in MEN_ALLOWED_ARTICLES
    if row["gender"] == "Women":
        return row["articleType"] in WOMEN_ALLOWED_ARTICLES
    return False

df = df[df.apply(_allowed, axis=1)].copy()
print(f"  After article filter  : {len(df)}")

df = df.dropna(subset=["id"])
df["id"] = df["id"].astype(int)

# ============================================================
# IMAGE VALIDATION
# ============================================================

print("\nValidating images …")
valid = []
for img_id in df["id"]:
    src = os.path.join(IMAGES_PATH, f"{img_id}.jpg")
    if os.path.exists(src) and cv2.imread(src) is not None:
        valid.append(img_id)

df = df[df["id"].isin(valid)].reset_index(drop=True)
print(f"  Valid images          : {len(df)}")

# ============================================================
# BALANCE  (up to 1500 per gender)
# ============================================================

PER_GENDER = 1500
men_df   = df[df["gender"] == "Men"].head(PER_GENDER)
women_df = df[df["gender"] == "Women"].head(PER_GENDER)
df       = pd.concat([men_df, women_df]).reset_index(drop=True)

print(f"\nFinal: {len(df)} rows  (Men={len(men_df)}  Women={len(women_df)})")

# ============================================================
# COPY IMAGES
# ============================================================

copied = 0
for img_id in df["id"]:
    src = os.path.join(IMAGES_PATH,     f"{img_id}.jpg")
    dst = os.path.join(FILTERED_IMAGES, f"{img_id}.jpg")
    if not os.path.exists(dst) and os.path.exists(src):
        shutil.copy2(src, dst)
        copied += 1

df.to_csv(FILTERED_CSV, index=False)

print("\n" + "=" * 60)
print("✅  DATASET FILTER COMPLETE")
print("=" * 60)
print(f"Images copied : {copied}")
print(f"CSV saved     : {FILTERED_CSV}")
print("=" * 60)

print("\nArticle-type breakdown:")
for at, cnt in df["articleType"].value_counts().head(35).items():
    g = df[df["articleType"] == at]["gender"].value_counts().to_dict()
    print(f"  {at:<30} {cnt:>5}  {g}")