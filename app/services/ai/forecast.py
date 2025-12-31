from datetime import datetime, timedelta
from typing import Dict, List, Optional

try:
    from app.services.odoo_connector import OdooConnector
except Exception:
    OdooConnector = None


def _extract_product_id(raw_pid) -> Optional[int]:
    if raw_pid is None:
        return None
    if isinstance(raw_pid, (list, tuple)) and raw_pid:
        raw_pid = raw_pid[0]
    try:
        return int(raw_pid)
    except Exception:
        return None


def _fetch_sales_lines(product_id: int, days: int = 180) -> List[Dict]:
    if not OdooConnector:
        return []
    from datetime import datetime
    conn = OdooConnector()
    date_from = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
    return conn.search_read(
        'sale.order.line',
        [['product_id', '=', product_id], ['create_date', '>=', date_from]],
        ['product_uom_qty', 'create_date'],
        limit=50000
    )


def _daily_series(lines: List[Dict], days: int) -> List[float]:
    today = datetime.utcnow().date()
    start = today - timedelta(days=days - 1)
    bucket = {start + timedelta(d): 0.0 for d in range(days)}
    for ln in lines:
        qty = float(ln.get('product_uom_qty', 0) or 0)
        dt_raw = ln.get('create_date')
        try:
            dt = datetime.fromisoformat(str(dt_raw).replace('Z', '+00:00')).date()
        except Exception:
            dt = today
        if dt in bucket:
            bucket[dt] += qty
    return [bucket[start + timedelta(d)] for d in range(days)]


def _smooth_ma(series: List[float], window: int = 7) -> List[float]:
    if window <= 1:
        return series[:]
    out = []
    acc = 0.0
    for i, v in enumerate(series):
        acc += v
        if i >= window:
            acc -= series[i - window]
        denom = min(i + 1, window)
        out.append(acc / denom)
    return out


def forecast_product(product_id: int, horizon_days: int = 30, lookback_days: int = 180) -> Dict:
    """Simple forecast using moving-average baseline and linear drift over last window.
    Returns daily forecast and totals for 7/30/90 days.
    """
    lines = _fetch_sales_lines(product_id=product_id, days=lookback_days)
    series = _daily_series(lines, days=min(lookback_days, 180)) if lines else []
    if not series:
        return {
            'product_id': product_id,
            'horizon_days': horizon_days,
            'daily_forecast': [0.0] * horizon_days,
            'totals': {'7d': 0.0, '30d': 0.0, '90d': 0.0}
        }
    smooth = _smooth_ma(series, window=7)
    baseline = smooth[-1]
    # drift as slope of last 14 days of smoothed series
    tail = smooth[-14:] if len(smooth) >= 14 else smooth
    drift = (tail[-1] - tail[0]) / max(1, len(tail))
    daily = []
    for d in range(horizon_days):
        val = max(0.0, baseline + drift * d)
        daily.append(round(val, 2))
    def sum_days(n: int) -> float:
        return round(sum(daily[:min(n, horizon_days)]), 2)
    return {
        'product_id': product_id,
        'horizon_days': horizon_days,
        'daily_forecast': daily,
        'totals': {
            '7d': sum_days(7),
            '30d': sum_days(30),
            '90d': sum_days(90),
        }
    }
