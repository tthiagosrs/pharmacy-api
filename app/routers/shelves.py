from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.dependencies import supabase, get_current_user

router = APIRouter(prefix="/shelves", tags=["Shelves"])


class ShelfCreate(BaseModel):
    name: str


class ShelfUpdate(BaseModel):
    name: str


class ReorderItem(BaseModel):
    id: str
    position: int


@router.get("")
def list_shelves(user=Depends(get_current_user)):
    result = (
        supabase.table("shelves")
        .select("id, name, position")
        .order("position")
        .execute()
    )
    return result.data


@router.post("")
def create_shelf(data: ShelfCreate, user=Depends(get_current_user)):
    max_pos = (
        supabase.table("shelves")
        .select("position")
        .order("position", desc=True)
        .limit(1)
        .execute()
    )
    next_pos = (max_pos.data[0]["position"] + 1) if max_pos.data else 0
    result = (
        supabase.table("shelves")
        .insert({"name": data.name, "position": next_pos})
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=500, detail="Erro ao criar prateleira")
    return result.data[0]


@router.put("/{shelf_id}")
def update_shelf(shelf_id: str, data: ShelfUpdate, user=Depends(get_current_user)):
    result = (
        supabase.table("shelves")
        .update({"name": data.name})
        .eq("id", shelf_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Prateleira não encontrada")
    return result.data[0]


@router.delete("/{shelf_id}")
def delete_shelf(shelf_id: str, user=Depends(get_current_user)):
    supabase.table("shelves").delete().eq("id", shelf_id).execute()
    return {"ok": True}


@router.patch("/reorder")
def reorder(items: list[ReorderItem], user=Depends(get_current_user)):
    for item in items:
        supabase.table("shelves").update({"position": item.position}).eq("id", item.id).execute()
    return {"ok": True}
