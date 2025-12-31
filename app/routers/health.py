from fastapi import APIRouter
from app.tasks.scheduler import sched
from app.services.odoo_connector import OdooConnector

router = APIRouter(prefix="/health", tags=["Health"]) 

@router.get("/app")
def app_health():
    return {
        'scheduler_running': bool(getattr(sched, 'running', False)),
    }

@router.get("/odoo")
def odoo_health():
    try:
        conn = OdooConnector()
        # minimal call
        _ = conn.search_read('res.company', [], ['name'], limit=1)
        return {'odoo_connection': 'ok'}
    except Exception as e:
        return {'odoo_connection': 'error', 'detail': str(e)}
