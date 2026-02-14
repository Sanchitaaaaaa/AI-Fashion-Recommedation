from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import user, recommend, wishlist

app = FastAPI(
    title="AI Fashion Recommendation API",
    description="AI-powered fashion recommendation system using body type and skin tone analysis",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user.router, prefix="/user", tags=["User"])
app.include_router(recommend.router, prefix="/recommend", tags=["Recommendations"])
app.include_router(wishlist.router, prefix="/wishlist", tags=["Wishlist"])

# ✅ Serve outfit images folder
app.mount("/outfit_images", StaticFiles(directory="outfit_images"), name="outfit_images")

# Health check endpoint
@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {"message": "AI Fashion Recommendation API Running"}

@app.get("/health")
async def health():
    """Health status"""
    return {
        "status": "healthy",
        "service": "AI Fashion Recommendation",
        "endpoints": {
            "users": "/user",
            "recommendations": "/recommend",
            "wishlist": "/wishlist"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
