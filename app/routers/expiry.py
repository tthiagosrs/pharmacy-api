from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.dependencies import supabase, get_current_user

router = APIRouter(prefix="/expiry", tags=["Expiry"])


class ExpiryCreate(BaseModel):
    product_id: str
    expiry_date: str
    shelf_id: str | None = None


class ExpiryUpdate(BaseModel):
    expiry_date: str | None = None
    shelf_id: str | None = None


class ReorderItem(BaseModel):
    id: str
    position: int


@router.post("")
def create_expiry(data: ExpiryCreate, user=Depends(get_current_user)):
    max_pos = (
        supabase.table("expiry_items")
        .select("position")
        .eq("product_id", data.product_id)
        .order("position", desc=True)
        .limit(1)
        .execute()
    )
    next_pos = (max_pos.data[0]["position"] + 1) if max_pos.data else 0

    payload = {
        "product_id": data.product_id,
        "expiry_date": data.expiry_date,
        "position": next_pos,
    }
    if data.shelf_id:
        payload["shelf_id"] = data.shelf_id

    result = supabase.table("expiry_items").insert(payload).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Erro ao adicionar validade")
    return result.data[0]


@router.patch("/{item_id}")
def update_expiry(item_id: str, data: ExpiryUpdate, user=Depends(get_current_user)):
    payload = {}
    if data.expiry_date is not None:
        payload["expiry_date"] = data.expiry_date
    if data.shelf_id is not None:
        payload["shelf_id"] = data.shelf_id

    if not payload:
        raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")

    result = (
        supabase.table("expiry_items")
        .update(payload)
        .eq("id", item_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    return result.data[0]


@router.delete("/{item_id}")
def delete_expiry(item_id: str, user=Depends(get_current_user)):
    supabase.table("expiry_items").delete().eq("id", item_id).execute()
    return {"ok": True}


@router.patch("/reorder")
def reorder(items: list[ReorderItem], user=Depends(get_current_user)):
    for item in items:
        supabase.table("expiry_items").update({"position": item.position}).eq("id", item.id).execute()
    return {"ok": True}
