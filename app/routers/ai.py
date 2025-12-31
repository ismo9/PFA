from fastapi import APIRouter
from app.services.ai_service import get_replenishment_recommendations
from app.services.ai.demand import predict_demand
from app.services.cache import cache
from app.services.odoo_connector import OdooConnector
from app.services.ai.segmentation import segment_abc_xyz
from app.services.ai.anomalies import detect_sales_anomalies
from app.services.ai.forecast import forecast_product
from app.services.ai.ml_forecast import forecast_with_model, train_product_model

router = APIRouter(prefix="/ai", tags=["AI"])

@router.get("/replenishment/recommendations", summary="AI-based stock replenishment")
def replenishment():
    return get_replenishment_recommendations()
@router.get("/replenishment/with_rop", summary="Replenishment with Reorder Point (ROP)")
def replenishment_with_rop(default_lead_time_days: int = 7, safety_stock_days: int = 3):
    """Augment replenishment recommendations with reorder point and suggested order quantity.
    ROP = avg_daily_sales * lead_time + safety_stock (approx as avg_daily_sales * safety_stock_days).
    """
    base = get_replenishment_recommendations() or {}
    items = base.get('replenishment_recommendations', [])
    for it in items:
        ads = float(it.get('avg_daily_sales', 0) or 0)
        stock = float(it.get('current_stock', 0) or 0)
        rop = ads * max(0, default_lead_time_days) + ads * max(0, safety_stock_days)
        suggested = max(0.0, round(rop - stock, 2))
        it['rop'] = round(rop, 2)
        it['suggested_order_qty'] = suggested
    base['rop_params'] = {
        'default_lead_time_days': default_lead_time_days,
        'safety_stock_days': safety_stock_days
    }
    return base


@router.get("/demand", summary="AI-based demand forecast (30d)")
def demand(lookback_days: int = 60, limit: int = 200):
    """Return per-product 30-day demand forecast with trend and confidence.

    - `lookback_days`: how many past days of sales to consider (capped inside to 90).
    - `limit`: maximum number of products returned.
    """
    # Cache by params
    cache_key = f"ai:demand:{lookback_days}:{limit}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        res = predict_demand(products=None, lookback_days=lookback_days) or []
    except Exception as exc:  # keep the endpoint robust
        return {"error": str(exc)}

    # Trim payload for large catalogs
    if limit and limit > 0:
        res = res[:limit]

    result = {"total": len(res), "items": res}
    cache.set(cache_key, result, ttl_seconds=90)
    return result

@router.get("/alerts")
def ai_alerts():
    conn = OdooConnector()
    products = conn.search_read("product.product", [], ["id", "name", "qty_available"])
    
    alerts = []
    
    # Check for low stock or out of stock
    for product in products:
        current_stock = product.get('qty_available', 0)
        
        if current_stock == 0:
            alerts.append({
                "type": "OUT_OF_STOCK",
                "product_id": product['id'],
                "product_name": product.get('name', ''),
                "message": "Product is out of stock"
            })
        elif current_stock < 10:
            alerts.append({
                "type": "LOW_STOCK",
                "product_id": product['id'],
                "product_name": product.get('name', ''),
                "message": f"Stock level low: {current_stock} units"
            })
    
    return {
        "total_alerts": len(alerts),
        "alerts": alerts
    }


@router.get("/segmentation", summary="ABC/XYZ product segmentation")
def segmentation(days: int = 60):
    cache_key = f"ai:segmentation:{days}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    res = segment_abc_xyz(days=days)
    cache.set(cache_key, res, ttl_seconds=120)
    return res


@router.get("/anomalies", summary="Sales anomalies (spikes/drops)")
def anomalies(days: int = 30, z: float = 3.0):
    cache_key = f"ai:anomalies:{days}:{z}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    res = detect_sales_anomalies(days=days, z_threshold=z)
    cache.set(cache_key, res, ttl_seconds=90)
    return res


@router.get("/forecast/{product_id}", summary="Per-product demand forecast")
def forecast(product_id: int, horizon_days: int = 30, lookback_days: int = 180):
    cache_key = f"ai:forecast:{product_id}:{horizon_days}:{lookback_days}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    # Prefer ML model if available; fallback to heuristic forecast
    res = forecast_with_model(product_id=product_id, horizon_days=horizon_days, lookback_days=lookback_days)
    if 'error' in res or (sum(res.get('daily_forecast', [])) == 0):
        res = forecast_product(product_id=product_id, horizon_days=horizon_days, lookback_days=lookback_days)
    cache.set(cache_key, res, ttl_seconds=120)
    return res
