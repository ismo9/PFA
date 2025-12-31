"""
KPI Builder Endpoints
Provides comprehensive metrics for custom dashboard creation
"""

from fastapi import APIRouter, Query, Depends
from typing import Optional, List
from datetime import datetime, timedelta
from app.services.odoo_connector import OdooConnector
from app.services.cache import cache
from app.auth import get_current_user, User

router = APIRouter(prefix="/kpi", tags=["KPI Metrics"])


def _calculate_date_range(days: int = 30):
    """Helper to get date range strings."""
    end = datetime.now()
    start = end - timedelta(days=days)
    return start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')


@router.get("/metrics")
def get_all_metrics(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user)
):
    """
    Get all available KPI metrics for dashboard builder.
    Returns comprehensive metrics across all categories.
    """
    cache_key = f"kpi_all_metrics_{days}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    connector = OdooConnector()
    start_date, end_date = _calculate_date_range(days)
    
    # Fetch all necessary data
    products = connector.search_read('product.product', [], ['name', 'list_price', 'qty_available', 'categ_id'])
    sales = connector.search_read('sale.order.line', [
        ('order_id.date_order', '>=', start_date),
        ('order_id.date_order', '<=', end_date),
        ('order_id.state', 'in', ['sale', 'done'])
    ], ['product_id', 'product_uom_qty', 'price_subtotal', 'order_id'])
    
    orders = connector.search_read('sale.order', [
        ('date_order', '>=', start_date),
        ('date_order', '<=', end_date),
        ('state', 'in', ['sale', 'done'])
    ], ['date_order', 'amount_total', 'state'])
    
    # Calculate metrics
    total_revenue = sum(s.get('price_subtotal', 0) for s in sales)
    total_orders = len(orders)
    total_qty = sum(s.get('product_uom_qty', 0) for s in sales)
    
    # Stock metrics
    total_stock_value = sum(p.get('qty_available', 0) * p.get('list_price', 0) for p in products)
    low_stock = sum(1 for p in products if p.get('qty_available', 0) < 10)
    out_of_stock = sum(1 for p in products if p.get('qty_available', 0) <= 0)
    active_products = len([p for p in products if any(s.get('product_id')[0] == p['id'] for s in sales if s.get('product_id'))])
    
    # Previous period for comparison (simple: double the days and compare)
    prev_start_date = (datetime.strptime(start_date, '%Y-%m-%d') - timedelta(days=days)).strftime('%Y-%m-%d')
    prev_sales = connector.search_read('sale.order.line', [
        ('order_id.date_order', '>=', prev_start_date),
        ('order_id.date_order', '<', start_date),
        ('order_id.state', 'in', ['sale', 'done'])
    ], ['price_subtotal'])
    prev_revenue = sum(s.get('price_subtotal', 0) for s in prev_sales)
    
    revenue_growth = ((total_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
    
    result = {
        "revenue_sales": {
            "total_revenue": round(total_revenue, 2),
            "revenue_growth_pct": round(revenue_growth, 2),
            "avg_order_value": round(total_revenue / total_orders, 2) if total_orders > 0 else 0,
            "gross_margin_pct": 35.0,  # Mock for demo (calculate from cost data if available)
            "revenue_per_product": round(total_revenue / active_products, 2) if active_products > 0 else 0
        },
        "orders_customers": {
            "total_orders": total_orders,
            "order_growth_pct": round((total_orders - len(prev_sales)) / len(prev_sales) * 100, 2) if prev_sales else 0,
            "avg_order_qty": round(total_qty / total_orders, 2) if total_orders > 0 else 0,
            "order_fulfillment_rate_pct": 95.0  # Mock
        },
        "inventory_stock": {
            "total_stock_value": round(total_stock_value, 2),
            "stock_turnover_ratio": round(total_revenue / total_stock_value, 2) if total_stock_value > 0 else 0,
            "low_stock_count": low_stock,
            "out_of_stock_count": out_of_stock,
            "stock_cover_days": 45,  # Mock (calculate from demand forecast)
            "products_under_rop": 12  # Mock
        },
        "products": {
            "active_products": active_products,
            "total_products": len(products),
            "new_products_30d": 5,  # Mock
            "sku_count": len(products),
            "avg_product_price": round(sum(p.get('list_price', 0) for p in products) / len(products), 2) if products else 0
        },
        "ai_forecasting": {
            "forecast_accuracy_smape": 0.15,  # Mock (fetch from ML models)
            "anomaly_count_7d": 3,  # Mock
            "anomaly_count_30d": 12,  # Mock
            "products_with_ml_models": 50,  # Mock
            "last_training_date": "2024-01-20T03:30:00"
        },
        "efficiency_operations": {
            "avg_lead_time_days": 7,  # Mock
            "order_cycle_time_days": 3,  # Mock
            "fulfillment_rate_pct": 95.0,
            "on_time_delivery_pct": 92.0
        },
        "period": {
            "days": days,
            "start_date": start_date,
            "end_date": end_date
        }
    }
    
    cache.set(cache_key, result, ttl=90)
    return result


@router.get("/metric/{metric_name}")
def get_specific_metric(
    metric_name: str,
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific KPI metric with historical data for charting.
    Example: /kpi/metric/total_revenue?days=90
    """
    cache_key = f"kpi_metric_{metric_name}_{days}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    connector = OdooConnector()
    start_date, end_date = _calculate_date_range(days)
    
    # Map metric names to calculations
    if metric_name == "total_revenue":
        sales = connector.search_read('sale.order.line', [
            ('order_id.date_order', '>=', start_date),
            ('order_id.date_order', '<=', end_date),
            ('order_id.state', 'in', ['sale', 'done'])
        ], ['price_subtotal', 'order_id'])
        
        value = sum(s.get('price_subtotal', 0) for s in sales)
        
        result = {
            "metric_name": "total_revenue",
            "value": round(value, 2),
            "unit": "currency",
            "trend": "up",  # Calculate from comparison
            "period_days": days
        }
    
    elif metric_name == "stock_value":
        products = connector.search_read('product.product', [], ['qty_available', 'list_price'])
        value = sum(p.get('qty_available', 0) * p.get('list_price', 0) for p in products)
        
        result = {
            "metric_name": "stock_value",
            "value": round(value, 2),
            "unit": "currency",
            "trend": "stable",
            "period_days": days
        }
    
    else:
        result = {
            "metric_name": metric_name,
            "value": 0,
            "unit": "unknown",
            "error": "Metric not implemented"
        }
    
    cache.set(cache_key, result, ttl=60)
    return result


@router.get("/comparison")
def compare_products(
    product_ids: str = Query(..., description="Comma-separated product IDs"),
    metrics: str = Query("revenue,quantity,margin", description="Comma-separated metric names"),
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user)
):
    """
    Compare multiple products across multiple metrics.
    Example: /kpi/comparison?product_ids=101,102,103&metrics=revenue,quantity&days=30
    """
    pid_list = [int(x.strip()) for x in product_ids.split(',')]
    metric_list = [x.strip() for x in metrics.split(',')]
    
    cache_key = f"kpi_comparison_{'_'.join(map(str, pid_list))}_{'_'.join(metric_list)}_{days}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    connector = OdooConnector()
    start_date, end_date = _calculate_date_range(days)
    
    result = {
        "products": [],
        "metrics": metric_list,
        "period_days": days
    }
    
    for pid in pid_list:
        product = connector.search_read('product.product', [('id', '=', pid)], ['name', 'list_price'])
        if not product:
            continue
        
        sales = connector.search_read('sale.order.line', [
            ('product_id', '=', pid),
            ('order_id.date_order', '>=', start_date),
            ('order_id.date_order', '<=', end_date),
            ('order_id.state', 'in', ['sale', 'done'])
        ], ['product_uom_qty', 'price_subtotal'])
        
        revenue = sum(s.get('price_subtotal', 0) for s in sales)
        quantity = sum(s.get('product_uom_qty', 0) for s in sales)
        
        product_data = {
            "product_id": pid,
            "product_name": product[0]['name'],
            "metrics": {}
        }
        
        if "revenue" in metric_list:
            product_data["metrics"]["revenue"] = round(revenue, 2)
        if "quantity" in metric_list:
            product_data["metrics"]["quantity"] = round(quantity, 2)
        if "margin" in metric_list:
            product_data["metrics"]["margin"] = 35.0  # Mock
        if "turnover" in metric_list:
            product_data["metrics"]["turnover"] = 12.5  # Mock
        
        result["products"].append(product_data)
    
    cache.set(cache_key, result, ttl=90)
    return result


@router.get("/catalog")
def get_metric_catalog():
    """
    Get the full catalog of available KPIs with metadata.
    Used by the KPI Builder UI to show available metrics.
    """
    return {
        "categories": [
            {
                "name": "Revenue & Sales",
                "metrics": [
                    {"id": "total_revenue", "label": "Total Revenue", "unit": "currency", "format": "currency"},
                    {"id": "revenue_growth", "label": "Revenue Growth", "unit": "percent", "format": "percentage"},
                    {"id": "gross_margin", "label": "Gross Margin", "unit": "percent", "format": "percentage"},
                    {"id": "avg_order_value", "label": "Avg Order Value", "unit": "currency", "format": "currency"},
                    {"id": "revenue_per_product", "label": "Revenue per Product", "unit": "currency", "format": "currency"}
                ]
            },
            {
                "name": "Orders & Customers",
                "metrics": [
                    {"id": "total_orders", "label": "Total Orders", "unit": "count", "format": "number"},
                    {"id": "order_growth", "label": "Order Growth", "unit": "percent", "format": "percentage"},
                    {"id": "fulfillment_rate", "label": "Fulfillment Rate", "unit": "percent", "format": "percentage"},
                    {"id": "backorder_pct", "label": "Backorder %", "unit": "percent", "format": "percentage"}
                ]
            },
            {
                "name": "Inventory & Stock",
                "metrics": [
                    {"id": "stock_value", "label": "Stock Value", "unit": "currency", "format": "currency"},
                    {"id": "turnover_ratio", "label": "Turnover Ratio", "unit": "ratio", "format": "decimal"},
                    {"id": "low_stock_count", "label": "Low Stock Items", "unit": "count", "format": "number"},
                    {"id": "out_stock_count", "label": "Out of Stock Items", "unit": "count", "format": "number"},
                    {"id": "stock_cover_days", "label": "Avg Stock Cover", "unit": "days", "format": "number"},
                    {"id": "under_rop_count", "label": "Products Under ROP", "unit": "count", "format": "number"}
                ]
            },
            {
                "name": "Products",
                "metrics": [
                    {"id": "active_products", "label": "Active Products", "unit": "count", "format": "number"},
                    {"id": "total_products", "label": "Total Products", "unit": "count", "format": "number"},
                    {"id": "new_products", "label": "New Products (30d)", "unit": "count", "format": "number"},
                    {"id": "avg_price", "label": "Avg Product Price", "unit": "currency", "format": "currency"}
                ]
            },
            {
                "name": "AI & Forecasting",
                "metrics": [
                    {"id": "forecast_smape", "label": "Forecast Accuracy (sMAPE)", "unit": "decimal", "format": "decimal"},
                    {"id": "anomaly_count_7d", "label": "Anomalies (7d)", "unit": "count", "format": "number"},
                    {"id": "anomaly_count_30d", "label": "Anomalies (30d)", "unit": "count", "format": "number"},
                    {"id": "ml_models_count", "label": "Products with ML", "unit": "count", "format": "number"}
                ]
            },
            {
                "name": "Efficiency & Operations",
                "metrics": [
                    {"id": "avg_lead_time", "label": "Avg Lead Time", "unit": "days", "format": "number"},
                    {"id": "cycle_time", "label": "Order Cycle Time", "unit": "days", "format": "number"},
                    {"id": "on_time_delivery", "label": "On-Time Delivery %", "unit": "percent", "format": "percentage"}
                ]
            }
        ],
        "total_metrics": 30
    }
