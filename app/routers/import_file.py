import io
from datetime import datetime, date

import openpyxl
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.dependencies import get_current_user, supabase

router = APIRouter(prefix="/products", tags=["Import"])


@router.post("/import")
async def import_products(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
):
    if not (file.filename or "").endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Apenas arquivos .xlsx são aceitos")

    contents = await file.read()
    try:
        wb = openpyxl.load_workbook(io.BytesIO(contents), data_only=True)
    except Exception:
        raise HTTPException(status_code=400, detail="Arquivo .xlsx inválido ou corrompido")

    ws = wb.active
    created = 0
    linked = 0
    skipped_no_date = 0
    skipped_duplicate = 0
    errors = []

    for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        if all(cell is None for cell in row):
            continue

        barcode = str(row[0]).strip() if row[0] is not None else ""
        name = str(row[1]).strip() if row[1] is not None else ""
        date_raw = row[2]

        if not name:
            errors.append({"row": row_idx, "reason": "Nome do produto ausente"})
            continue

        if date_raw is None or str(date_raw).strip() == "":
            skipped_no_date += 1
            continue

        try:
            if isinstance(date_raw, (datetime, date)):
                expiry_date = (
                    date_raw.strftime("%Y-%m-%d")
                    if isinstance(date_raw, datetime)
                    else date_raw.isoformat()
                )
            else:
                expiry_date = datetime.strptime(str(date_raw).strip(), "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            errors.append({"row": row_idx, "reason": f"Data inválida: '{date_raw}' (esperado dd/mm/aaaa)"})
            continue

        product_id = None

        if barcode:
            res = supabase.table("product_barcodes").select("product_id").eq("barcode", barcode).execute()
            if res.data:
                product_id = res.data[0]["product_id"]

        if not product_id:
            res = supabase.table("products").select("id").ilike("name", name).limit(1).execute()
            if res.data:
                product_id = res.data[0]["id"]

        if not product_id:
            res = supabase.table("products").insert({"name": name}).execute()
            product_id = res.data[0]["id"]
            if barcode:
                supabase.table("product_barcodes").insert(
                    {"product_id": product_id, "barcode": barcode}
                ).execute()
            created += 1
        else:
            linked += 1
            if barcode:
                dup_bc = supabase.table("product_barcodes").select("id").eq("barcode", barcode).execute()
                if not dup_bc.data:
                    supabase.table("product_barcodes").insert(
                        {"product_id": product_id, "barcode": barcode}
                    ).execute()

        dup = (
            supabase.table("expiry_items")
            .select("id")
            .eq("product_id", product_id)
            .eq("expiry_date", expiry_date)
            .execute()
        )
        if dup.data:
            skipped_duplicate += 1
            continue

        supabase.table("expiry_items").insert(
            {"product_id": product_id, "expiry_date": expiry_date}
        ).execute()

    return {
        "created": created,
        "linked": linked,
        "skipped_no_date": skipped_no_date,
        "skipped_duplicate": skipped_duplicate,
        "errors": errors,
    }
