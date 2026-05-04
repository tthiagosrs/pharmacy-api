from fastapi import FastAPI
from app.routers import auth

app = FastAPI(title="FarmaOS API", version="1.0.0")

app.include_router(auth.router)

@app.get("/")
def home():
    return {"app": "FarmaOS", "status": "online", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "ok", "database": "connected"}