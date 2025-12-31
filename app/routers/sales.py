from fastapi import APIRouter, HTTPException
from app.services.odoo_connector import OdooConnector

router = APIRouter(prefix="/sales", tags=["sales"])

@router.get("/", summary="List sales orders")
def list_sales(limit: int = 0):
    conn = OdooConnector()
    try:
        sales = conn.get_sales(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    out = []
    for s in sales:
        partner = s.get('partner_id') or [None, None]
        out.append({
            "id": s.get("id"),
            "name": s.get("name"),
            "customer": partner[1] if partner else None,
            "date_order": s.get("date_order"),
            "amount_total": s.get("amount_total")
        })
    return out
