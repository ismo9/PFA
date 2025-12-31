from fastapi import APIRouter, HTTPException, Query
from app.services.odoo_connector import OdooConnector
from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Dict, Any, Optional, Literal
from app.services.cache import cache

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
@router.get("/abcxyz_summary", summary="ABC/XYZ segmentation summary")
def abcxyz_summary(days: int = 60):
    from app.services.ai.segmentation import segment_abc_xyz
    res = segment_abc_xyz(days=days)
    a=b=c=0
    x=y=z=0
    for item in res.get('items', []):
        if item['abc'] == 'A': a += 1
        elif item['abc'] == 'B': b += 1
        else: c += 1
        if item['xyz'] == 'X': x += 1
        elif item['xyz'] == 'Y': y += 1
        else: z += 1
    return {
        'days_lookback': days,
        'abc': {'A': a, 'B': b, 'C': c},
        'xyz': {'X': x, 'Y': y, 'Z': z},
    }


def parse_date(d: Optional[str]) -> Optional[datetime]:
    if not d:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(d[:19], fmt)
        except Exception:
            continue
    try:
        return datetime.fromisoformat(d)
    except Exception:
        return None


def _extract_product_id(raw_pid) -> Optional[int]:
    if raw_pid is None:
        return None
    if isinstance(raw_pid, (list, tuple)) and raw_pid:
        raw_pid = raw_pid[0]
    try:
        return int(raw_pid)
    except Exception:
        return None


@router.get("/overview", summary="Key metrics overview (optimized)")
def overview():
    """Return high-level dashboard metrics: total products, stock value, alerts, recent sales."""
    conn = OdooConnector()
    
    # Fetch all products with stock and pricing
    products = conn.search_read(
        "product.product",
        [],
        ["id", "name", "qty_available", "standard_price"],
        limit=10000
    )
    
    total_products = len(products)
    total_stock_value = sum(
        p.get("qty_available", 0) * p.get("standard_price", 0) 
        for p in products
    )
    
    low_stock_count = sum(1 for p in products if 0 < p.get("qty_available", 0) < 10)
    out_of_stock_count = sum(1 for p in products if p.get("qty_available", 0) == 0)
    
    # Recent sales (last 7 days)
    date_from = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
    recent_sales = conn.search_read(
        "sale.order.line",
        [["create_date", ">=", date_from]],
        ["product_uom_qty", "price_total"],
        limit=50000
    )
    
    total_recent_qty = sum(ln.get("product_uom_qty", 0) for ln in recent_sales)
    total_recent_revenue = sum(ln.get("price_total", 0) for ln in recent_sales)
    
    result = {
        "total_products": total_products,
        "total_stock_value": round(total_stock_value, 2),
        "low_stock_alerts": low_stock_count,
        "out_of_stock_alerts": out_of_stock_count,
        "recent_sales_7d": {
            "quantity_sold": round(total_recent_qty, 2),
            "revenue": round(total_recent_revenue, 2)
        }
    }
    cache.set("dashboard:overview", result, ttl_seconds=90)
    return result


@router.get("/sales_trends", summary="Sales trends over time (optimized)")
def sales_trends(
    period: Literal["daily", "weekly", "monthly"] = Query("daily", description="Aggregation period"),
    days: int = Query(30, description="Number of days to look back", ge=1, le=365)
):
    """Return sales aggregated by period (daily/weekly/monthly) over the last N days."""
    # Cache by parameters
    cache_key = f"dashboard:sales_trends:{period}:{days}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    conn = OdooConnector()
    
    date_from = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
    lines = conn.search_read(
        "sale.order.line",
        [["create_date", ">=", date_from]],
        ["product_uom_qty", "price_total", "create_date"],
        limit=50000
    )
    
    # Group by period
    buckets = defaultdict(lambda: {"quantity": 0.0, "revenue": 0.0})
    
    for ln in lines:
        dt = parse_date(ln.get("create_date"))
        if not dt:
            continue
        
        if period == "daily":
            key = dt.date().isoformat()
        elif period == "weekly":
            # ISO week: year-week
            key = f"{dt.isocalendar()[0]}-W{dt.isocalendar()[1]:02d}"
        else:  # monthly
            key = f"{dt.year}-{dt.month:02d}"
        
        buckets[key]["quantity"] += ln.get("product_uom_qty", 0)
        buckets[key]["revenue"] += ln.get("price_total", 0)
    
    # Convert to sorted list
    trends = [
        {
            "period": k,
            "quantity_sold": round(v["quantity"], 2),
            "revenue": round(v["revenue"], 2)
        }
        for k, v in sorted(buckets.items())
    ]
    
    result = {
        "period_type": period,
        "days_lookback": days,
        "total_periods": len(trends),
        "trends": trends
    }
    cache.set(cache_key, result, ttl_seconds=90)
    return result


@router.get("/top_products", summary="Top products by sales (optimized)")
def top_products(
    metric: Literal["quantity", "revenue"] = Query("quantity", description="Sort by quantity or revenue"),
    days: int = Query(30, description="Number of days to look back", ge=1, le=365),
    limit: int = Query(10, description="Number of top products to return", ge=1, le=100)
):
    """Return top N products ranked by sales quantity or revenue over last N days."""
    cache_key = f"dashboard:top_products:{metric}:{days}:{limit}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    conn = OdooConnector()
    
    date_from = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
    lines = conn.search_read(
        "sale.order.line",
        [["create_date", ">=", date_from]],
        ["product_id", "product_uom_qty", "price_total"],
        limit=50000
    )
    
    # Aggregate by product
    product_stats = defaultdict(lambda: {"quantity": 0.0, "revenue": 0.0})
    
    for ln in lines:
        pid = _extract_product_id(ln.get("product_id"))
        if pid is None:
            continue
        product_stats[pid]["quantity"] += ln.get("product_uom_qty", 0)
        product_stats[pid]["revenue"] += ln.get("price_total", 0)
    
    # Sort by chosen metric
    sorted_products = sorted(
        product_stats.items(),
        key=lambda x: x[1][metric],
        reverse=True
    )[:limit]
    
    # Fetch product names
    product_ids = [pid for pid, _ in sorted_products]
    if product_ids:
        products_info = conn.search_read(
            "product.product",
            [["id", "in", product_ids]],
            ["id", "name"]
        )
        name_map = {p["id"]: p.get("name", f"Product {p['id']}") for p in products_info}
    else:
        name_map = {}
    
    top = [
        {
            "product_id": pid,
            "product_name": name_map.get(pid, f"Product {pid}"),
            "quantity_sold": round(stats["quantity"], 2),
            "revenue": round(stats["revenue"], 2)
        }
        for pid, stats in sorted_products
    ]
    
    result = {
        "metric": metric,
        "days_lookback": days,
        "total_results": len(top),
        "products": top
    }
    cache.set(cache_key, result, ttl_seconds=90)
    return result


@router.get("/stock_status", summary="Inventory distribution by stock level (optimized)")
def stock_status():
    """Return product counts and samples by stock category: out-of-stock, low, adequate, overstock."""
    cache_key = "dashboard:stock_status"
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    conn = OdooConnector()
    
    products = conn.search_read(
        "product.product",
        [],
        ["id", "name", "qty_available"],
        limit=10000
    )
    
    out_of_stock = []
    low_stock = []
    adequate = []
    overstock = []
    
    for p in products:
        qty = p.get("qty_available", 0)
        pid = p.get("id")
        name = p.get("name", f"Product {pid}")
        
        if qty == 0:
            out_of_stock.append({"product_id": pid, "product_name": name, "quantity": qty})
        elif qty < 10:
            low_stock.append({"product_id": pid, "product_name": name, "quantity": qty})
        elif qty < 100:
            adequate.append({"product_id": pid, "product_name": name, "quantity": qty})
        else:
            overstock.append({"product_id": pid, "product_name": name, "quantity": qty})
    
    result = {
        "out_of_stock": {
            "count": len(out_of_stock),
            "samples": out_of_stock[:10]
        },
        "low_stock": {
            "count": len(low_stock),
            "samples": low_stock[:10]
        },
        "adequate": {
            "count": len(adequate),
            "samples": adequate[:10]
        },
        "overstock": {
            "count": len(overstock),
            "samples": overstock[:10]
        }
    }
    cache.set(cache_key, result, ttl_seconds=90)
    return result


@router.get("/summary", summary="KPI global summary (legacy)")
def dashboard_summary():
    """
    Retourne un résumé des KPIs principaux :
    - total_products, total_stock_qty, stock_value_estimated,
    - total_sales_amount, total_purchases_amount,
    - total_customers, total_vendors
    """
    conn = OdooConnector()
    try:
        # Products
        prod_fields = ['id', 'list_price', 'qty_available', 'forecasted_quantity']
        prods = conn.search_read('product.product', [], prod_fields)
        total_products = len(prods)
        total_stock_qty = 0.0
        stock_value_estimated = 0.0
        for p in prods:
            qty = p.get('qty_available') or 0.0
            price = p.get('list_price') or 0.0
            total_stock_qty += qty
            stock_value_estimated += qty * price

        # Sales total
        sales = conn.search_read('sale.order', [], ['amount_total'])
        total_sales_amount = sum([s.get('amount_total') or 0.0 for s in sales])

        # Purchases total
        purchases = conn.search_read('purchase.order', [], ['amount_total'])
        total_purchases_amount = sum([p.get('amount_total') or 0.0 for p in purchases])

        # Customers & Vendors (Odoo 13+ uses customer_rank / supplier_rank)
        customers = conn.search_read('res.partner', [['customer_rank', '>', 0]], ['id'])
        vendors = conn.search_read('res.partner', [['supplier_rank', '>', 0]], ['id'])
        total_customers = len(customers)
        total_vendors = len(vendors)

        return {
            "total_products": total_products,
            "total_stock_qty": total_stock_qty,
            "stock_value_estimated": round(stock_value_estimated, 2),
            "total_sales_amount": round(total_sales_amount, 2),
            "total_purchases_amount": round(total_purchases_amount, 2),
            "total_customers": total_customers,
            "total_vendors": total_vendors,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sales/monthly", summary="Sales aggregated per month")
def sales_monthly(months: int = Query(12, description="Nombre de mois à remonter (défaut 12)")):
    """
    Retourne la somme des ventes par mois (dernier `months` mois).
    """
    conn = OdooConnector()
    try:
        sales = conn.search_read('sale.order', [], ['date_order', 'amount_total'])
        agg: Dict[str, float] = defaultdict(float)
        for s in sales:
            d = parse_date(s.get('date_order'))
            if not d:
                continue
            key = f"{d.year}-{d.month:02d}"
            agg[key] += float(s.get('amount_total') or 0.0)
        # keep only last `months` keys sorted
        sorted_keys = sorted(agg.keys())
        # return last `months` entries
        items = [{"month": k, "amount": round(agg[k], 2)} for k in sorted_keys][-months:]
        return {"months": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sales/top-products", summary="Top selling products (by qty)")
def sales_top_products(limit: int = Query(10, description="Top N products")):
    """
    Retourne les produits les plus vendus (somme des quantités sur sale.order.line).
    """
    conn = OdooConnector()
    try:
        lines = conn.search_read('sale.order.line', [], ['product_id', 'product_uom_qty'])
        agg_qty: Dict[int, Dict[str, Any]] = {}
        for l in lines:
            prod = l.get('product_id')
            if not prod:
                continue
            pid = prod[0]
            pname = prod[1] if len(prod) > 1 else str(pid)
            qty = float(l.get('product_uom_qty') or 0.0)
            if pid not in agg_qty:
                agg_qty[pid] = {"product_id": pid, "product_name": pname, "qty": 0.0}
            agg_qty[pid]["qty"] += qty
        top = sorted(agg_qty.values(), key=lambda x: x["qty"], reverse=True)[:limit]
        for t in top:
            t["qty"] = round(t["qty"], 2)
        return {"top_products": top}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sales/by-customer", summary="Sales aggregated by customer")
def sales_by_customer(limit: int = Query(20, description="Return top N customers by sales")):
    conn = OdooConnector()
    try:
        orders = conn.search_read('sale.order', [], ['partner_id', 'amount_total'])
        agg: Dict[int, Dict[str, Any]] = {}
        for o in orders:
            partner = o.get('partner_id')
            if not partner:
                continue
            pid = partner[0]
            pname = partner[1] if len(partner) > 1 else str(pid)
            amt = float(o.get('amount_total') or 0.0)
            if pid not in agg:
                agg[pid] = {"partner_id": pid, "partner_name": pname, "amount": 0.0}
            agg[pid]["amount"] += amt
        top = sorted(agg.values(), key=lambda x: x["amount"], reverse=True)[:limit]
        for t in top:
            t["amount"] = round(t["amount"], 2)
        return {"by_customer": top}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/purchases/monthly", summary="Purchases aggregated per month")
def purchases_monthly(months: int = Query(12, description="Nombre de mois à remonter")):
    conn = OdooConnector()
    try:
        purchases = conn.search_read('purchase.order', [], ['date_order', 'amount_total'])
        agg: Dict[str, float] = defaultdict(float)
        for p in purchases:
            d = parse_date(p.get('date_order'))
            if not d:
                continue
            key = f"{d.year}-{d.month:02d}"
            agg[key] += float(p.get('amount_total') or 0.0)
        sorted_keys = sorted(agg.keys())
        items = [{"month": k, "amount": round(agg[k], 2)} for k in sorted_keys][-months:]
        return {"months": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/purchases/by-vendor", summary="Purchases aggregated by vendor")
def purchases_by_vendor(limit: int = Query(20, description="Top N vendors by purchases")):
    conn = OdooConnector()
    try:
        orders = conn.search_read('purchase.order', [], ['partner_id', 'amount_total'])
        agg: Dict[int, Dict[str, Any]] = {}
        for o in orders:
            partner = o.get('partner_id')
            if not partner:
                continue
            pid = partner[0]
            pname = partner[1] if len(partner) > 1 else str(pid)
            amt = float(o.get('amount_total') or 0.0)
            if pid not in agg:
                agg[pid] = {"vendor_id": pid, "vendor_name": pname, "amount": 0.0}
            agg[pid]["amount"] += amt
        top = sorted(agg.values(), key=lambda x: x["amount"], reverse=True)[:limit]
        for t in top:
            t["amount"] = round(t["amount"], 2)
        return {"by_vendor": top}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stock/low", summary="Low stock alerts")
def stock_low(threshold: int = Query(5, description="Seuil de stock faible")):
    """
    Retourne la liste des produits dont available_quantity <= threshold.
    """
    conn = OdooConnector()
    try:
        prods = conn.search_read('product.product', [], ['id', 'name', 'qty_available', 'list_price'])
        low = []
        for p in prods:
            qty = float(p.get('qty_available') or 0.0)
            if qty <= threshold:
                low.append({
                    "product_id": p.get('id'),
                    "product_name": p.get('name'),
                    "qty_available": qty,
                    "list_price": p.get('list_price') or 0.0
                })
        # sort by lowest stock first
        low_sorted = sorted(low, key=lambda x: x["qty_available"])
        return {"low_stock": low_sorted}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/stock/top-movements", summary="Top moved products by moved quantity")
def stock_top_movements(limit: int = Query(20, description="Top N products by moved qty")):
    conn = OdooConnector()
    try:
        moves = conn.search_read('stock.move', [], ['product_id', 'product_uom_qty', 'quantity', 'location_id', 'location_dest_id'])
        agg: Dict[int, Dict[str, Any]] = {}
        for m in moves:
            prod = m.get('product_id')
            if not prod:
                continue
            pid = prod[0]
            pname = prod[1] if len(prod) > 1 else str(pid)
            qty = float(m.get('product_uom_qty') or m.get('quantity') or 0.0)
            if pid not in agg:
                agg[pid] = {"product_id": pid, "product_name": pname, "moved_qty": 0.0}
            agg[pid]["moved_qty"] += qty
        top = sorted(agg.values(), key=lambda x: x["moved_qty"], reverse=True)[:limit]
        for t in top:
            t["moved_qty"] = round(t["moved_qty"], 2)
        return {"top_moved_products": top}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
