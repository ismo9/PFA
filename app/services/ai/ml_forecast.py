from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
import numpy as np
from joblib import dump, load

try:
    from app.services.odoo_connector import OdooConnector
except Exception:
    OdooConnector = None

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'models', 'forecasts')
os.makedirs(MODELS_DIR, exist_ok=True)


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
    conn = OdooConnector()
    date_from = (datetime.utcnow() - timedelta(days=days)).strftime('%Y-%m-%d')
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


def _moving_average(series: List[float], window: int = 7) -> List[float]:
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


def _model_path(product_id: int) -> str:
    return os.path.join(MODELS_DIR, f'product_{product_id}.joblib')


def train_product_model(product_id: int, lookback_days: int = 180) -> Dict:
    """Train a simple ML model (LinearRegression) on smoothed daily quantities.
    Features: time index and optional polynomial term for drift.
    """
    try:
        from sklearn.linear_model import LinearRegression
        from sklearn.preprocessing import PolynomialFeatures
        from sklearn.pipeline import Pipeline
        from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error
    except Exception:
        return {'error': 'scikit-learn not available'}

    lines = _fetch_sales_lines(product_id, days=lookback_days)
    series = _daily_series(lines, days=min(lookback_days, 180)) if lines else []
    if len(series) < 14:
        return {'product_id': product_id, 'trained': False, 'reason': 'insufficient_history'}

    y = np.array(_moving_average(series, window=7))
    X = np.arange(len(y)).reshape(-1, 1)

    model = Pipeline([
        ('poly', PolynomialFeatures(degree=2, include_bias=False)),
        ('lr', LinearRegression()),
    ])
    model.fit(X, y)

    y_pred = model.predict(X)
    mae = float(mean_absolute_error(y, y_pred))
    try:
        mape = float(mean_absolute_percentage_error(y, y_pred)) if y.sum() > 0 else None
    except Exception:
        mape = None
    # sMAPE handles zeros better
    denom = (np.abs(y) + np.abs(y_pred))
    smape = float(np.mean(2.0 * np.abs(y - y_pred) / np.where(denom == 0, 1.0, denom)))

    dump(model, _model_path(product_id))

    return {
        'product_id': product_id,
        'trained': True,
        'samples': len(y),
        'metrics': {
            'mae': round(mae, 3),
            'mape': round(mape, 3) if mape is not None else None,
            'smape': round(smape, 3)
        },
        'model_type': 'LinearRegression(poly=2)'
    }


def forecast_with_model(product_id: int, horizon_days: int = 30, lookback_days: int = 180) -> Dict:
    """Use saved model to forecast the next `horizon_days`.
    If no model exists, train on the fly.
    """
    path = _model_path(product_id)
    if not os.path.exists(path):
        train_product_model(product_id, lookback_days=lookback_days)

    try:
        model = load(path)
    except Exception:
        return {'product_id': product_id, 'error': 'model_load_failed'}

    lines = _fetch_sales_lines(product_id, days=lookback_days)
    series = _daily_series(lines, days=min(lookback_days, 180)) if lines else []
    if not series:
        return {'product_id': product_id, 'horizon_days': horizon_days, 'daily_forecast': [0.0]*horizon_days}

    y = np.array(_moving_average(series, window=7))
    X = np.arange(len(y)).reshape(-1, 1)
    # Extend time index for forecast
    X_future = np.arange(len(y), len(y) + horizon_days).reshape(-1, 1)
    y_future = model.predict(X_future)
    daily = [float(max(0.0, round(v, 2))) for v in y_future]
    # Confidence intervals from residual stddev
    y_hist_pred = model.predict(X)
    resid = y - y_hist_pred
    sigma = float(np.std(resid)) if resid.size else 0.0
    ci = {
        'low': [float(max(0.0, round(v - 1.96 * sigma, 2))) for v in y_future],
        'high': [float(max(0.0, round(v + 1.96 * sigma, 2))) for v in y_future]
    }

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
        },
        'model_type': 'LinearRegression(poly=2)',
        'confidence_interval': ci
    }
