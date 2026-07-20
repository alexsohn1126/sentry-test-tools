import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def fetch_order_details(order_id, coupon=None):
    order = {
        "order_id": order_id,
        "items": [
            {"sku": "WIDGET-42", "qty": 2, "price": 19.99},
            {"sku": "GADGET-7", "qty": 1, "price": 49.99},
        ],
        "customer": {"id": 12, "name": "Alex"},
        "status": "processing",
        "shipped_at": None,
    }
    if coupon is not None:
        logger.info("coupon was none", order_id, coupon)
        order["coupon"] = coupon
    response = json.dumps(order)
    return json.loads(response)


def get_discount(order):
    return order.get("coupon", {}).get("percent", 0) / 100


def error():
    order = fetch_order_details("ORD-20260212-1847")
    total = sum(item["price"] * item["qty"] for item in order["items"])
    discount = get_discount(order)
    final_price = total * (1 - discount)
