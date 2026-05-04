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


@router.post("/login")
def login(data: LoginInput):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password
        })
        return {
            "access_token": response.session.access_token,
            "user_id": str(response.user.id),
            "email": response.user.email
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail="Email ou senha inválidos")


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