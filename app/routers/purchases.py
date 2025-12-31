from fastapi import APIRouter, HTTPException
from app.services.odoo_connector import OdooConnector

router = APIRouter(prefix="/purchases", tags=["purchases"])

@router.get("/", summary="List purchase orders")
def list_purchases(limit: int = 0):
    conn = OdooConnector()
    try:
        purchases = conn.get_purchases(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    out = []
    for p in purchases:
        partner = p.get('partner_id') or [None, None]
        out.append({
            "id": p.get("id"),
            "name": p.get("name"),
            "vendor": partner[1] if partner else None,
            "date_order": p.get("date_order"),
            "amount_total": p.get("amount_total")
        })
    return out
