from fastapi import APIRouter, HTTPException
from app.services.odoo_connector import OdooConnector

router = APIRouter(prefix="/inventory", tags=["inventory"])

@router.get("/moves", summary="List stock moves")
def list_moves(limit: int = 0):
    conn = OdooConnector()
    try:
        moves = conn.get_stock_moves(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    out = []
    for m in moves:
        product = m.get('product_id') or [None, None]
        src = m.get('location_id') or [None, None]
        dst = m.get('location_dest_id') or [None, None]
        out.append({
            "id": m.get("id"),
            "name": m.get("name"),
            "product": product[1] if product else None,
            "quantity": m.get("product_qty"),
            "source_location": src[1] if src else None,
            "dest_location": dst[1] if dst else None,
            "date": m.get("date"),
            "state": m.get("state")
        })
    return out
