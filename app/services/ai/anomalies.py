from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict

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


def _fetch_sales(days: int = 30, limit: int = 50000) -> List[Dict]:
    if not OdooConnector:
        return []
    conn = OdooConnector()
    date_from = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
    return conn.search_read(
        'sale.order.line',
        [['create_date', '>=', date_from]],
        ['product_id', 'product_uom_qty', 'create_date'],
        limit=limit
    )


def detect_sales_anomalies(days: int = 30, z_threshold: float = 3.0) -> Dict:
    """Detect sales spikes/drops via z-score over daily quantity per product.
    Returns anomalies with severity and direction.
    """
    lines = _fetch_sales(days=days)

    # Build per-product per-day quantities
    daily_by_product: Dict[int, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for ln in lines:
        pid = _extract_product_id(ln.get('product_id'))
        if pid is None:
            continue
        dt = str(ln.get('create_date'))[:10]
        qty = float(ln.get('product_uom_qty', 0) or 0)
        daily_by_product[pid][dt] += qty

    anomalies = []
    for pid, day_map in daily_by_product.items():
        days_sorted = sorted(day_map.keys())
        series = [day_map[d] for d in days_sorted]
        if len(series) < 7:
            continue
        mean = sum(series) / len(series)
        var = (sum((x-mean)**2 for x in series) / len(series)) ** 0.5
        for d in days_sorted:
            x = day_map[d]
            if var == 0:
                z = 0
            else:
                z = (x - mean) / var
            if abs(z) >= z_threshold:
                anomalies.append({
                    'product_id': pid,
                    'date': d,
                    'quantity': round(x, 2),
                    'z_score': round(z, 2),
                    'direction': 'SPIKE' if z > 0 else 'DROP',
                    'severity': 'HIGH' if abs(z) >= 4 else 'MEDIUM'
                })
    return {'days_lookback': days, 'total': len(anomalies), 'items': anomalies}
