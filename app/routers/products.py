from fastapi import APIRouter, Depends, HTTPException
from app.services.odoo_connector import OdooConnector

router = APIRouter(prefix="/products", tags=["products"])

def get_connector():
    return OdooConnector()

@router.get("/", summary="List products")
def list_products(limit: int = 0):
    conn = get_connector()
    try:
        prods = conn.get_products(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    # Normalize response
    out = []
    for p in prods:
        out.append({
            "id": p.get("id"),
            "name": p.get("name"),
            "internal_ref": p.get("default_code"),
            "price": p.get("list_price"),
            "cost": p.get("standard_price"),
            "qty_on_hand": p.get("qty_available"),
            "forecasted": p.get("virtual_available"),
            "type": p.get("type"),
            "category": p.get("categ_id")[1] if p.get("categ_id") else None
        })
    return out
