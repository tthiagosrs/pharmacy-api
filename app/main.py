from fastapi import FastAPI

app = FastAPI(
    title="FarmaOS API",
    version="1.0.0"
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
    return {"status": "ok"}