from fastapi import FastAPI
from app.routers import ai, products, sales, purchases, invoices, inventory, dashboard, health, auth as auth_router, kpi
from app.config import settings
from fastapi import HTTPException
import xmlrpc.client

from app.tasks.scheduler import shutdown_scheduler, start_scheduler  

# Odoo connection setup
ODOO_URL = settings.ODOO_URL
ODOO_DB = settings.ODOO_DB
ODOO_USERNAME = settings.ODOO_USERNAME
ODOO_PASSWORD = settings.ODOO_PASSWORD

common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')


app = FastAPI(title="ERPConnect API", version="0.1")

# Enable CORS for frontend
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    # start scheduler in background
    try:
        start_scheduler()
    except Exception as e:
        pass

@app.on_event("shutdown")
def on_shutdown():
    try:
        shutdown_scheduler()
    except Exception:
        pass

app.include_router(auth_router.router)
app.include_router(products.router)
app.include_router(sales.router)
app.include_router(purchases.router)
app.include_router(invoices.router)
app.include_router(inventory.router)
app.include_router(dashboard.router)
app.include_router(health.router)
app.include_router(ai.router)
app.include_router(kpi.router)

@app.get("/")
def root():
    return {"service": "ERPConnect API", "odoo_url": settings.ODOO_URL, "db": settings.ODOO_DB}


# ✅ GET all products
@app.get("/products")
def get_products():
    try:
        products = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'product.product', 'search_read',
            [[]],
            {'fields': ['id', 'name', 'default_code', 'list_price', 'qty_available', 'virtual_available']}
        )
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ GET product by ID
@app.get("/products/{product_id}")
def get_product(product_id: int):
    try:
        product = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'product.product', 'search_read',
            [[['id', '=', product_id]]],
            {'fields': ['id', 'name', 'default_code', 'list_price', 'qty_available', 'virtual_available']}
        )
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ GET product stock info
@app.get("/products/{product_id}/stock")
def get_product_stock(product_id: int):
    try:
        stock = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'product.product', 'search_read',
            [[['id', '=', product_id]]],
            {'fields': ['qty_available', 'virtual_available']}
        )
        if not stock:
            raise HTTPException(status_code=404, detail="Product not found")
        return stock[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ GET sales history for a product
@app.get("/products/{product_id}/sales")
def get_product_sales(product_id: int):
    try:
        sales = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'sale.order.line', 'search_read',
            [[['product_id', '=', product_id]]],
            {'fields': ['order_id', 'product_uom_qty', 'price_unit', 'create_date']}
        )
        return sales
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ GET purchase history for a product
@app.get("/products/{product_id}/purchases")
def get_product_purchases(product_id: int):
    try:
        purchases = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'purchase.order.line', 'search_read',
            [[['product_id', '=', product_id]]],
            {'fields': ['order_id', 'product_qty', 'price_unit', 'create_date']}
        )
        return purchases
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
