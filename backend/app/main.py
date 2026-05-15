from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routes import (
    user,
    recommend,
    wishlist,
)

app = FastAPI(
    title="AI Fashion Recommendation API",
    description=(
        "AI-powered fashion recommendation system "
        "using image similarity, body type, skin tone, "
        "and occasion analysis. Dataset: Myntra (Kaggle)."
    ),
    version="2.0.0",
)

# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# ROUTERS
# ============================================================

app.include_router(user.router,      prefix="/user",      tags=["User"])
app.include_router(recommend.router, prefix="/recommend", tags=["Recommendations"])
app.include_router(wishlist.router,  prefix="/wishlist",  tags=["Wishlist"])

# ============================================================
# STATIC FILES
# ============================================================

app.mount(
    "/fashion_images",
    StaticFiles(directory="fashion_dataset/filtered_images"),
    name="fashion_images",
)

app.mount(
    "/uploads",
    StaticFiles(directory="storage/uploads"),
    name="uploads",
)

# ============================================================
# HEALTH ROUTES
# ============================================================

@app.get("/")
async def root():
    return {
        "message" : "AI Fashion Recommendation API Running",
        "version" : "2.0.0",
        "dataset" : "Myntra Fashion Dataset (Kaggle)",
        "filters" : {
            "gender"         : "Men and Women only (no Kids)",
            "categories"     : "Apparel only (no Footwear / Accessories)",
            "subcategories"  : "Topwear, Bottomwear, Dress, Saree, Suits …",
        },
        "features": [
            "Gender-aware recommendations",
            "Occasion filtering",
            "Body type matching",
            "Skin tone analysis",
            "Image similarity search",
        ],
    }


@app.get("/health")
async def health():
    return {
        "status"    : "healthy",
        "service"   : "AI Fashion Recommendation",
        "dataset"   : "Myntra Dataset",
        "endpoints" : {
            "users"          : "/user",
            "recommendations": "/recommend",
            "wishlist"       : "/wishlist",
            "fashion_images" : "/fashion_images/{image_name}",
        },
    }


# ============================================================
# ENTRYPOINT
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)