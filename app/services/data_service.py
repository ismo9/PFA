# app/services/data_service.py

from typing import List, Dict, Any, Optional
from app.services.odoo_connector import OdooConnector
from datetime import datetime, timedelta
from logging_config import logger


class DataService:
    def __init__(self):
        self.conn = OdooConnector()

    # -------------------------------
    # PRODUCTS
    # -------------------------------
    def get_products(self, limit: int = 0) -> List[Dict[str, Any]]:
        fields = [
            'id',
            'name',
            'default_code',
            'list_price',
            'standard_price',
            'qty_available',
            'virtual_available'
        ]
        return self.conn.search_read('product.product', [], fields, limit)

    # -------------------------------
    # SALES
    # -------------------------------
    def get_product_sales_last_days(self, product_id: int, days: int = 30) -> float:
        """
        Return total sold quantity for a product over last N days.
        """
        try:
            date_from = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            domain = [
                ['product_id', '=', product_id],
                ['create_date', '>=', date_from]
            ]

            lines = self.conn.search_read(
                'sale.order.line',
                domain,
                ['product_uom_qty']
            )

            return sum(l.get('product_uom_qty', 0.0) for l in lines)

        except Exception:
            logger.exception("Failed to fetch sales data")
            return 0.0

    def get_product_sales_lines(self, product_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """
        Return sales lines for a product over last N days.
        """
        try:
            date_from = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            domain = [
                ['product_id', '=', product_id],
                ['create_date', '>=', date_from]
            ]

            return self.conn.search_read(
                'sale.order.line',
                domain,
                ['product_uom_qty', 'create_date']
            )
        except Exception:
            logger.exception("Failed to fetch sales lines")
            return []

    # -------------------------------
    # STOCK
    # -------------------------------
    def get_product_stock(self, product_id: int) -> Dict[str, Any]:
        fields = ['qty_available', 'virtual_available']
        result = self.conn.search_read(
            'product.product',
            [['id', '=', product_id]],
            fields
        )
        return result[0] if result else {}


# Singleton
_data_service = None


def get_data_service() -> DataService:
    global _data_service
    if _data_service is None:
        _data_service = DataService()
    return _data_service


# Convenience wrappers
def get_all_products(limit: int = 0) -> List[Dict[str, Any]]:
    return get_data_service().get_products(limit)


def get_product_sales_lines(product_id: int, days: int = 30) -> List[Dict[str, Any]]:
    return get_data_service().get_product_sales_lines(product_id, days)


def get_product_stock(product_id: int) -> Dict[str, Any]:
    return get_data_service().get_product_stock(product_id)
