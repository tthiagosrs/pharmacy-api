from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.dependencies import supabase, get_current_user

router = APIRouter(prefix="/products", tags=["Products"])


class ProductCreate(BaseModel):
    name: str
    barcode: str | None = None


class BarcodeAdd(BaseModel):
    barcode: str


class ProductUpdate(BaseModel):
    name: str


class ReorderItem(BaseModel):
    id: str
    position: int


@router.get("/active")
def list_active(user=Depends(get_current_user)):
    rows = (
        supabase.table("expiry_items")
        .select(
            "id, expiry_date, position, "
            "products(id, name, position, product_barcodes(barcode)), "
            "shelves(id, name)"
        )
        .order("position")
        .execute()
    )

    groups: dict = {}
    for row in rows.data:
        product = row["products"]
        pid = product["id"]
        if pid not in groups:
            groups[pid] = {
                "id": pid,
                "name": product["name"],
                "position": product["position"],
                "barcodes": [b["barcode"] for b in product.get("product_barcodes") or []],
                "items": [],
            }
        groups[pid]["items"].append({
            "id": row["id"],
            "expiry_date": row["expiry_date"],
            "position": row["position"],
            "shelf": row["shelves"],
        })

    return sorted(groups.values(), key=lambda p: p["position"])


@router.get("/search")
def search(q: str = "", user=Depends(get_current_user)):
    if not q:
        return []
    result = (
        supabase.table("products")
        .select("id, name")
        .ilike("name", f"%{q}%")
        .limit(10)
        .execute()
    )
    return result.data


@router.get("/barcode/{barcode}")
def lookup_barcode(barcode: str, user=Depends(get_current_user)):
    result = (
        supabase.table("product_barcodes")
        .select("products(id, name, position)")
        .eq("barcode", barcode)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Código de barras não encontrado")
    return result.data[0]["products"]


@router.post("")
def create_product(data: ProductCreate, user=Depends(get_current_user)):
    if data.barcode:
        existing = (
            supabase.table("product_barcodes")
            .select("products(id, name, position)")
            .eq("barcode", data.barcode)
            .execute()
        )
        if existing.data:
            return existing.data[0]["products"]

    max_pos = (
        supabase.table("products")
        .select("position")
        .order("position", desc=True)
        .limit(1)
        .execute()
    )
    next_pos = (max_pos.data[0]["position"] + 1) if max_pos.data else 0

    product = (
        supabase.table("products")
        .insert({"name": data.name, "position": next_pos})
        .execute()
    )
    if not product.data:
        raise HTTPException(status_code=500, detail="Erro ao criar produto")

    if data.barcode:
        supabase.table("product_barcodes").insert({
            "product_id": product.data[0]["id"],
            "barcode": data.barcode,
        }).execute()

    return product.data[0]


@router.post("/{product_id}/barcodes")
def add_barcode(product_id: str, data: BarcodeAdd, user=Depends(get_current_user)):
    existing = (
        supabase.table("product_barcodes")
        .select("id")
        .eq("barcode", data.barcode)
        .execute()
    )
    if existing.data:
        raise HTTPException(status_code=409, detail="Código de barras já cadastrado")

    result = (
        supabase.table("product_barcodes")
        .insert({"product_id": product_id, "barcode": data.barcode})
        .execute()
    )
    return result.data[0]


@router.delete("/{product_id}/barcodes/{barcode}")
def remove_barcode(product_id: str, barcode: str, user=Depends(get_current_user)):
    supabase.table("product_barcodes").delete().eq("product_id", product_id).eq(
        "barcode", barcode
    ).execute()
    return {"ok": True}


@router.patch("/reorder")
def reorder(items: list[ReorderItem], user=Depends(get_current_user)):
    for item in items:
        supabase.table("products").update({"position": item.position}).eq("id", item.id).execute()
    return {"ok": True}


@router.patch("/{product_id}")
def update_product(product_id: str, data: ProductUpdate, user=Depends(get_current_user)):
    result = (
        supabase.table("products")
        .update({"name": data.name})
        .eq("id", product_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return result.data[0]
