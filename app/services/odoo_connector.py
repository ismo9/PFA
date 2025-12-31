import xmlrpc.client
from typing import List, Dict, Any
from app.config import settings

class OdooConnector:
    def __init__(self):
        self.url = settings.ODOO_URL.rstrip("/")
        self.db = settings.ODOO_DB
        self.username = settings.ODOO_USERNAME
        self.password = settings.ODOO_PASSWORD
        self._uid = None
        self._common = None
        self._models = None
        self.authenticate()

    def authenticate(self):
        self._common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")
        self._uid = self._common.authenticate(self.db, self.username, self.password, {})
        if not self._uid:
            raise RuntimeError("Odoo authentication failed. Check credentials and DB.")
        self._models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")

    def execute_kw(self, model: str, method: str, args: List = None, kwargs: Dict = None):
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
        
        # Try up to 3 times with fresh connections
        for attempt in range(3):
            try:
                # Create a fresh connection for each attempt
                models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")
                res = models.execute_kw(self.db, self._uid, self.password, model, method, args, kwargs)
                return res
            except Exception as e:
                if attempt == 2:  # Last attempt
                    raise e
                # Re-authenticate on failure
                self.authenticate()

    def search_read(self, model: str, domain: List = None, fields: List = None, limit: int = 0) -> List[Dict[str, Any]]:
        if domain is None:
            domain = []
        if fields is None:
            fields = []
        return self.execute_kw(model, 'search_read', [domain], {'fields': fields, 'limit': limit})

    # Convenience helpers
    def get_products(self, limit: int = 0):
        fields = ['id', 'name', 'default_code', 'list_price', 'standard_price', 'qty_available', 'virtual_available', 'type', 'categ_id']
        return self.search_read('product.product', [], fields, limit)

    def get_sales(self, limit: int = 0):
        fields = ['id', 'name', 'partner_id', 'date_order', 'amount_total']
        return self.search_read('sale.order', [], fields, limit)

    def get_purchases(self, limit: int = 0):
        fields = ['id', 'name', 'partner_id', 'date_order', 'amount_total']
        return self.search_read('purchase.order', [], fields, limit)

    def get_invoices(self, limit: int = 0):
        fields = ['id', 'name', 'partner_id', 'invoice_date', 'amount_total', 'state']
        return self.search_read('account.move', [['move_type', 'in', ['out_invoice','in_invoice']]], fields, limit)

    def get_stock_moves(self, limit: int = 0):
        fields = [
            'id',
            'product_id',
            'product_uom_qty',
            'quantity',
            'location_id',
            'location_dest_id',
            'reference',
            'state',
            'date',
            'picking_id',
            'picking_type_id',
        ]
        return self.search_read('stock.move', [], fields, limit)

