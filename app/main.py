import os
from fastapi import FastAPI
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="FarmaOS API",
    version="1.0.0"
)

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
)

@app.get("/")
def home():
    return {
        "app": "FarmaOS",
        "status": "online",
        "version": "1.0.0"
    }

@app.get("/health")
def health():
    return {
        "status": "ok",
        "database": "connected"
    }

@app.get("/modules")
def modules():
    return {
        "modules": [
            {"name": "estoque", "status": "active"},
            {"name": "clinico", "status": "active"},
            {"name": "financeiro", "status": "active"},
            {"name": "crm", "status": "active"}
        ]
    }