import os
from fastapi import Header, HTTPException
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
)


def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token inválido")
    token = authorization.removeprefix("Bearer ")
    try:
        result = supabase.auth.get_user(token)
        return result.user
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
