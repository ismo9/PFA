# app/routers/sync.py
from fastapi import APIRouter, HTTPException
import xmlrpc.client
import csv
from datetime import datetime
from math import isfinite
from app.config import settings

router = APIRouter(prefix="/sync", tags=["sync"])

@router.post("/odoo-sales", summary="Sync sales from Odoo and write sales_history.csv")
def sync_odoo_sales():
    try:
        ODOO_URL = settings.ODOO_URL
        DB = settings.ODOO_DB
        USERNAME = settings.ODOO_USERNAME
        PASSWORD = settings.ODOO_PASSWORD
        OUT_CSV = "sales_history.csv"

        common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
        uid = common.authenticate(DB, USERNAME, PASSWORD, {})
        if not uid:
            raise HTTPException(status_code=500, detail="Odoo authentication failed")
        models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

        orders = models.execute_kw(DB, uid, PASSWORD, 'sale.order', 'search_read',
                                   [[]], {'fields': ['id', 'name', 'date_order', 'partner_id', 'state'], 'limit': 0})

        rows_written = 0
        with open(OUT_CSV, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['product_id', 'product_name', 'order_id', 'order_name', 'order_date',
                             'qty', 'price_unit', 'partner_id', 'partner_name'])

            for o in orders:
                o_id = o['id']
                o_name = o.get('name')
                date_order = o.get('date_order') or o.get('create_date') or datetime.utcnow().isoformat()
                partner = o.get('partner_id') or [None, None]
                partner_id = partner[0] if isinstance(partner, list) else None
                partner_name = partner[1] if isinstance(partner, list) else partner

                lines = models.execute_kw(DB, uid, PASSWORD, 'sale.order.line', 'search_read',
                                          [[['order_id', '=', o_id]]],
                                          {'fields': ['id', 'product_id', 'product_uom_qty', 'price_unit', 'create_date'], 'limit': 0})
                for ln in lines:
                    product = ln.get('product_id') or [None, None]
                    product_id = product[0] if isinstance(product, list) else product
                    product_name = product[1] if isinstance(product, list) else product
                    qty = ln.get('product_uom_qty') or 0
                    price_unit = ln.get('price_unit') or 0
                    create_date = ln.get('create_date') or date_order
                    try:
                        qty_val = float(qty)
                    except Exception:
                        qty_val = 0.0
                    try:
                        price_val = float(price_unit)
                    except Exception:
                        price_val = 0.0
                    if not isfinite(qty_val) or qty_val == 0:
                        continue
                    writer.writerow([product_id, product_name, o_id, o_name, create_date, qty_val, price_val, partner_id, partner_name])
                    rows_written += 1

        return {"status": "ok", "rows": rows_written, "csv": OUT_CSV}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
