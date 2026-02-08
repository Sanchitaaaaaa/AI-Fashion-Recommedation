from fastapi import FastAPI
from app.routes import recommend

app = FastAPI()

app.include_router(recommend.router)

@app.get("/")
def root():
    return {"message": "Backend is running"}
