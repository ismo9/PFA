from fastapi import APIRouter, HTTPException
from app.services.odoo_connector import OdooConnector

router = APIRouter(prefix="/invoices", tags=["invoices"])

@router.get("/", summary="List invoices")
def list_invoices(limit: int = 0):
    conn = OdooConnector()
    try:
        invoices = conn.get_invoices(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    out = []
    for inv in invoices:
        partner = inv.get('partner_id') or [None, None]
        out.append({
            "id": inv.get("id"),
            "name": inv.get("name"),
            "partner": partner[1] if partner else None,
            "invoice_date": inv.get("invoice_date"),
            "amount_total": inv.get("amount_total"),
            "state": inv.get("state")
        })
    return out
