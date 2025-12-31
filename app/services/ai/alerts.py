def sales_drop_alert(monthly_sales):
    if len(monthly_sales) < 3:
        return None

    last = monthly_sales[-1]
    avg = sum(monthly_sales[-3:]) / 3

    if last < avg * 0.75:
        return "Sales dropped more than 25%"

    return None


def generate_alerts(products, sales, stock):
    """
    Generate alerts based on products, sales, and stock data.
    """
    alerts = []
    
    # Check for low stock
    for product in products:
        product_id = product['id']
        current_stock = product.get('qty_available', 0)
        
        # Alert if stock is very low (less than 10 units)
        if current_stock < 10 and current_stock > 0:
            alerts.append({
                "type": "LOW_STOCK",
                "product_id": product_id,
                "product_name": product.get('name', ''),
                "message": f"Stock level low: {current_stock} units"
            })
        
        # Alert if stock is zero
        elif current_stock == 0:
            alerts.append({
                "type": "OUT_OF_STOCK",
                "product_id": product_id,
                "product_name": product.get('name', ''),
                "message": "Product is out of stock"
            })
    
    return alerts