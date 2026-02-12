from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import user, recommend

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router, prefix="/user", tags=["User"])
app.include_router(recommend.router, prefix="/recommend", tags=["Recommend"])

@app.get("/")
def root():
    return {"message": "AI Fashion Recommendation API Running"}
