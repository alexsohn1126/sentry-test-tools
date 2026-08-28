import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def fetch_order_details(order_id):
    response = json.dumps({
        "order_id": order_id,
        "items": [
            {"sku": "WIDGET-42", "qty": 2, "price": 19.99},
            {"sku": "GADGET-7", "qty": 1, "price": 49.99},
        ],
        "customer": {"id": 12, "name": "Alex"},
        "status": "processing",
        "shipped_at": None,
    })
    return json.loads(response)


def error():
    order = fetch_order_details("ORD-20260212-1847")
    total = sum(item["price"] * item["qty"] for item in order["items"])
    coupon = order.get("coupon")
    if coupon is None:
        logger.warning("Order %s has no coupon; applying zero discount.", order.get("order_id"))
        percent = 0
    elif "percent" not in coupon:
        logger.warning("Coupon for order %s is missing 'percent' field; applying zero discount.", order.get("order_id"))
        percent = 0
    else:
        percent = coupon["percent"]
    discount = percent / 100
    final_price = total * (1 - discount)
