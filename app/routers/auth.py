from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.dependencies import supabase

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginInput(BaseModel):
    email: str
    password: str


class RegisterInput(BaseModel):
    email: str
    password: str
    name: str
    role: str


class RefreshInput(BaseModel):
    refresh_token: str


@router.post("/login")
def login(data: LoginInput):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password
        })
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "user_id": str(response.user.id),
            "email": response.user.email
        }
    except Exception:
        raise HTTPException(status_code=401, detail="Email ou senha inválidos")


@router.post("/refresh")
def refresh(data: RefreshInput):
    try:
        response = supabase.auth.refresh_session(data.refresh_token)
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
        }
    except Exception:
        raise HTTPException(status_code=401, detail="Sessão expirada")


@router.post("/register")
def register(data: RegisterInput):
    try:
        response = supabase.auth.sign_up({
            "email": data.email,
            "password": data.password,
            "options": {
                "data": {
                    "name": data.name,
                    "role": data.role
                }
            }
        })
        return {
            "message": "Usuário cadastrado com sucesso",
            "user_id": str(response.user.id),
            "email": response.user.email
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/profile")
def profile(token: str):
    try:
        user = supabase.auth.get_user(token)
        result = supabase.table("profiles").select("*").eq(
            "id", str(user.user.id)
        ).single().execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token inválido")