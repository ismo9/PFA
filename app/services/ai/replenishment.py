import numpy as np
from datetime import datetime

ENGINE_NAME = "rule-based-replenishment-v3"

def replenishment(products):
    results = []

    daily_demands = [
        p.get("avg_daily_sales", 0)
        for p in products
        if p.get("avg_daily_sales", 0) > 0
    ]

    if not daily_demands:
        return {
            "engine": ENGINE_NAME,
            "generated_at": datetime.utcnow().isoformat(),
            "replenishment_recommendations": []
        }

    p50 = np.percentile(daily_demands, 50)
    p70 = np.percentile(daily_demands, 70)
    p85 = np.percentile(daily_demands, 85)

    for p in products:
        pid = p["id"]
        name = p["name"]
        stock = float(p.get("current_stock", 0))
        raw_daily = float(p.get("avg_daily_sales", 0))

        effective_daily = min(raw_daily, p70) if raw_daily > 0 else 0

        if raw_daily >= p85:
            category = "FAST"
            target_days = 30
        elif raw_daily >= p50:
            category = "NORMAL"
            target_days = 45
        else:
            category = "SLOW"
            target_days = 60

        days_of_cover = (
            stock / effective_daily
            if effective_daily > 0 else float("inf")
        )

        if days_of_cover < 10:
            decision = "REORDER"
            risk = "HIGH"
        elif days_of_cover < 25:
            decision = "MONITOR"
            risk = "MEDIUM"
        else:
            decision = "OK"
            risk = "LOW"

        target_stock = effective_daily * target_days
        reorder_qty = max(0, target_stock - stock)

        max_reorder = effective_daily * 60
        reorder_qty = min(reorder_qty, max_reorder)

        confidence = round(min(1, raw_daily / p70), 2) if p70 > 0 else 0.5

        results.append({
            "product_id": pid,
            "product_name": name,
            "category": category,
            "current_stock": round(stock, 2),
            "avg_daily_sales": round(raw_daily, 2),
            "effective_daily_demand": round(effective_daily, 2),
            "days_of_cover": round(days_of_cover, 1) if days_of_cover != float("inf") else None,
            "recommended_qty": int(reorder_qty),
            "decision": decision,
            "risk_level": risk,
            "confidence_score": confidence,
            "explanation": (
                f"{category} product with target {target_days} days coverage. "
                "Demand capped using portfolio percentile."
            )
        })

    return {
        "engine": ENGINE_NAME,
        "generated_at": datetime.utcnow().isoformat(),
        "total_products_analyzed": len(results),
        "replenishment_recommendations": results
    }
