from fastapi import FastAPI

app = FastAPI(
    title="FarmaOS API",
    description="Sistema de gestão para farmácias",
    version="1.0.0"
)

@app.get("/")
def home():
    return {
        "app": "FarmaOS",
        "version": "1.0.0",
        "status": "online"
    }

@app.get("/health")
def health():
    return {
        "status": "ok",
        "database": "pending"
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

@app.get("/estoque")
def estoque():
    return {
        "produtos": [
            {"id": 1, "nome": "Dipirona 500mg", "quantidade": 150, "validade": "2026-08-01"},
            {"id": 2, "nome": "Amoxicilina 875mg", "quantidade": 80, "validade": "2026-05-15"},
            {"id": 3, "nome": "Omeprazol 20mg", "quantidade": 200, "validade": "2027-01-10"}
        ]
    }