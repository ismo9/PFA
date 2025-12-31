# app/tasks/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from app.services.ai_service import AIService
from app.services.ai.ml_forecast import train_product_model
from app.services.odoo_connector import OdooConnector
from datetime import datetime, timedelta
from logging_config import logger

svc = AIService()
sched = BackgroundScheduler()

def job_train_all():
    logger.info("Scheduler: starting train_all job")
    try:
        res = svc.train_all_products(limit=0)
        logger.info("Scheduler: train_all completed: %s", res)
    except Exception as e:
        logger.exception("Scheduler train_all failed: %s", e)


def job_train_top_ml():
    logger.info("Scheduler: training ML models for top products")
    try:
        conn = OdooConnector()
        date_from = (datetime.utcnow() - timedelta(days=60)).strftime("%Y-%m-%d")
        lines = conn.search_read(
            'sale.order.line',
            [['create_date', '>=', date_from]],
            ['product_id', 'product_uom_qty'],
            limit=50000
        )
        from collections import defaultdict
        qty_by_pid = defaultdict(float)
        for ln in lines:
            prod = ln.get('product_id')
            pid = prod[0] if isinstance(prod, (list, tuple)) and prod else prod
            if pid is None:
                continue
            qty_by_pid[int(pid)] += float(ln.get('product_uom_qty', 0) or 0)
        top_ids = [pid for pid, _ in sorted(qty_by_pid.items(), key=lambda x: x[1], reverse=True)[:50]]
        for pid in top_ids:
            train_product_model(product_id=pid, lookback_days=180)
        logger.info("Scheduler: ML training done for %d products", len(top_ids))
    except Exception as e:
        logger.exception("Scheduler ML training failed: %s", e)

# schedule once every night at 03:00
# AI training nightly
sched.add_job(job_train_all, 'cron', hour=3, minute=0)
# ML forecast models nightly (3:30)
sched.add_job(job_train_top_ml, 'cron', hour=3, minute=30)

def start_scheduler():
    if not sched.running:
        logger.info("Starting APScheduler")
        sched.start()

def shutdown_scheduler():
    if sched.running:
        logger.info("Shutting down APScheduler")
        sched.shutdown()
