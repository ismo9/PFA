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


def _fetch_sales(days: int = 60, limit: int = 50000) -> List[Dict]:
    if not OdooConnector:
        return []
    conn = OdooConnector()
    date_from = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
    return conn.search_read(
        'sale.order.line',
        [['create_date', '>=', date_from]],
        ['product_id', 'product_uom_qty', 'price_total', 'create_date'],
        limit=limit
    )


def _fetch_products(product_ids: List[int]) -> Dict[int, str]:
    if not OdooConnector or not product_ids:
        return {}
    conn = OdooConnector()
    items = conn.search_read('product.product', [['id', 'in', product_ids]], ['id', 'name'])
    return {p['id']: p.get('name', f"Product {p['id']}") for p in items}


def segment_abc_xyz(days: int = 60) -> Dict:
    """Classify products into ABC (value) and XYZ (variability) segments.
    - ABC by revenue percentile (A top 20%, B next 30%, C rest)
    - XYZ by demand variability (std/mean): X low (<0.3), Y medium (0.3-0.7), Z high (>0.7)
    """
    lines = _fetch_sales(days=days)
    revenue_by_product: Dict[int, float] = defaultdict(float)
    demand_by_product: Dict[int, List[float]] = defaultdict(list)
    
    # Aggregate revenue and build simple per-line demand (fallback per-day later if needed)
    for ln in lines:
        pid = _extract_product_id(ln.get('product_id'))
        if pid is None:
            continue
        qty = float(ln.get('product_uom_qty', 0) or 0)
        rev = float(ln.get('price_total', 0) or 0)
        revenue_by_product[pid] += rev
        demand_by_product[pid].append(qty)
    
    # ABC by revenue percentiles
    pairs = sorted([(pid, revenue) for pid, revenue in revenue_by_product.items()], key=lambda x: x[1], reverse=True)
    n = max(1, len(pairs))
    def abc_rank(i: int) -> str:
        pct = (i+1) / n
        if pct <= 0.2:
            return 'A'
        elif pct <= 0.5:
            return 'B'
        return 'C'
    
    # XYZ by variability (std/mean) of qty across lines
    def xyz_rank(series: List[float]) -> str:
        if not series:
            return 'Z'
        mean = sum(series)/len(series)
        var = (sum((x-mean)**2 for x in series)/len(series))**0.5
        ratio = var/(mean+1e-6) if mean>0 else 1.0
        if ratio < 0.3:
            return 'X'
        elif ratio < 0.7:
            return 'Y'
        else:
            return 'Z'
    
    result = []
    for i, (pid, revenue) in enumerate(pairs):
        abc = abc_rank(i)
        xyz = xyz_rank(demand_by_product.get(pid, []))
        result.append({'product_id': pid, 'abc': abc, 'xyz': xyz, 'revenue': round(revenue, 2)})
    
    names = _fetch_products([pid for pid,_ in pairs])
    for r in result:
        r['product_name'] = names.get(r['product_id'], f"Product {r['product_id']}")
    
    return {
        'days_lookback': days,
        'total': len(result),
        'items': result
    }
