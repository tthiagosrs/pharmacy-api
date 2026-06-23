from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, products, shelves, expiry, import_file

app = FastAPI(title="FarmaOS API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(shelves.router)
app.include_router(expiry.router)
app.include_router(import_file.router)

@app.get("/", tags=["Health"], summary="Status da API")
def home():
    return {"app": "FarmaOS", "status": "online", "version": "1.0.0"}

@app.get("/health", tags=["Health"], summary="Health Check")
def health():
    return {"status": "ok", "database": "connected"}