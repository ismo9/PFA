from datetime import datetime, timedelta
from typing import List, Dict, Optional

try:
    # Prefer using our data service wrappers if available
    from app.services.data_service import (
        get_all_products as ds_get_all_products,
        get_product_sales_lines as ds_get_product_sales_lines,
    )
except Exception:
    # Fallback stubs if import fails (keeps module importable)
    ds_get_all_products = None
    ds_get_product_sales_lines = None

try:
    from app.services.odoo_connector import OdooConnector
except Exception:
    OdooConnector = None


def _moving_average(series: List[float], window: int = 7) -> List[float]:
    if window <= 1 or len(series) == 0:
        return series[:]
    out: List[float] = []
    acc = 0.0
    for i, v in enumerate(series):
        acc += v
        if i >= window:
            acc -= series[i - window]
        denom = min(i + 1, window)
        out.append(acc / denom)
    return out


def _trend_strength(series: List[float]) -> float:
    # Simple slope between last and first smoothed values
    if not series:
        return 0.0
    s = _moving_average(series, window=7)
    return (s[-1] - s[0]) / (len(s) or 1)


def _confidence_from_data(days_covered: int, variability: float, samples: int) -> float:
    # Heuristic confidence: more coverage, lower variability, more samples => higher confidence
    base = min(1.0, max(0.2, days_covered / 30.0))
    var_penalty = max(0.5, 1.0 - min(1.0, variability))
    sample_boost = min(1.0, 0.5 + min(0.5, samples / 50.0))
    conf = base * 0.4 + var_penalty * 0.3 + sample_boost * 0.3
    return round(min(0.98, max(0.2, conf)), 2)


def _daily_series_from_sales(lines: List[Dict], days: int) -> List[float]:
    # Build a per-day quantity series
    today = datetime.utcnow().date()
    start = today - timedelta(days=days - 1)
    bucket = {start + timedelta(d): 0.0 for d in range(days)}
    for ln in lines:
        qty = float(ln.get("product_uom_qty", 0) or 0)
        dt_raw = ln.get("create_date") or ln.get("date_order")
        try:
            # Odoo returns string timestamps; attempt to parse
            dt = datetime.fromisoformat(str(dt_raw).replace("Z", "+00:00")).date()
        except Exception:
            dt = today
        if dt in bucket:
            bucket[dt] += qty
    # Return in chronological order
    return [bucket[start + timedelta(d)] for d in range(days)]


def _extract_product_id(raw_pid) -> Optional[int]:
    if raw_pid is None:
        return None
    if isinstance(raw_pid, (list, tuple)) and raw_pid:
        # Odoo may return [id, name]
        raw_pid = raw_pid[0]
    try:
        return int(raw_pid)
    except Exception:
        return None


def _fetch_sales_lines_bulk(days: int = 60, limit: int = 10000) -> List[Dict]:
    if not OdooConnector:
        return []
    try:
        conn = OdooConnector()
        date_from = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
        domain = [['create_date', '>=', date_from]]
        return conn.search_read(
            'sale.order.line',
            domain,
            ['product_id', 'product_uom_qty', 'create_date'],
            limit=limit
        )
    except Exception:
        return []


def predict_demand(products: Optional[List[Dict]] = None, lookback_days: int = 60) -> List[Dict]:
    """Predict 30-day demand using recent sales history.

    - If `products` is None, fetch a reasonable set via data_service.
    - Uses a moving-average of daily sales over `lookback_days` to estimate current daily demand.
    - Computes a simple trend and confidence score.
    """
    predictions: List[Dict] = []

    # Fetch products if not provided
    if products is None:
        if ds_get_all_products:
            products = ds_get_all_products(limit=500) or []
        else:
            products = []

    # Bulk-fetch sales lines once to avoid per-product XML-RPC calls
    bulk_lines = _fetch_sales_lines_bulk(days=lookback_days)
    lines_by_product: Dict[int, List[Dict]] = {}
    for ln in bulk_lines:
        pid = _extract_product_id(ln.get('product_id'))
        if pid is None:
            continue
        lines_by_product.setdefault(pid, []).append(ln)

    for p in products:
        pid = p.get("id")
        name = p.get("name") or p.get("display_name") or f"Product {pid}"

        # Prefer bulk-fetched lines; fallback to per-product fetch only if needed
        lines: List[Dict] = lines_by_product.get(pid, [])
        if not lines and ds_get_product_sales_lines and pid is not None:
            try:
                lines = ds_get_product_sales_lines(product_id=pid, days=lookback_days) or []
            except Exception:
                lines = []

        series = _daily_series_from_sales(lines, days=min(lookback_days, 90)) if lines else []

        if series:
            smooth = _moving_average(series, window=7)
            current_daily = smooth[-1]
            # Variability as normalized stddev over mean
            mean = sum(series) / (len(series) or 1)
            var = (sum((x - mean) ** 2 for x in series) / (len(series) or 1)) ** 0.5
            variability = (var / (mean + 1e-6)) if mean > 0 else 1.0
            trend_slope = _trend_strength(series)
            days_covered = len(series)
            confidence = _confidence_from_data(days_covered, variability, samples=len(lines))
        else:
            # Fallback to provided avg_daily_sales if history is missing
            current_daily = float(p.get("avg_daily_sales", 0) or 0)
            trend_slope = 0.0
            confidence = 0.6 if current_daily > 0 else 0.3

        next_30 = max(0.0, current_daily) * 30.0

        if trend_slope > 0.2:
            trend = "UP"
        elif trend_slope < -0.2:
            trend = "DOWN"
        else:
            trend = "STABLE"

        predictions.append({
            "product_id": pid,
            "product_name": name,
            "predicted_30d_demand": round(next_30, 2),
            "trend": trend,
            "confidence": confidence,
        })

    return predictions
