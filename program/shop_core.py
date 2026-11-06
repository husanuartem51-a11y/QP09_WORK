"""Offline educational calculation model. All data are synthetic."""
import json
from pathlib import Path
PRODUCTS = {p["id"]: p for p in json.loads(Path(__file__).with_name("products.json").read_text(encoding="utf-8"))}
class RuleError(ValueError):
    def __init__(self, code):
        super().__init__(code)
        self.code = code

def quote(items, promo="", fulfillment="delivery", version="reference"):
    if version not in ("reference", "candidate"):
        raise RuleError("VERSION")
    if not isinstance(items, list) or not items:
        raise RuleError("EMPTY_CART")
    if fulfillment not in ("delivery", "pickup"):
        raise RuleError("FULFILLMENT")
    if not isinstance(promo, str):
        raise RuleError("PROMO")
    code = promo.strip().upper()
    if code not in ("", "STUDY10"):
        raise RuleError("PROMO")
    quantities = {}
    for item in items:
        if not isinstance(item, dict) or item.get("id") not in PRODUCTS:
            raise RuleError("PRODUCT")
        q = item.get("quantity")
        if type(q) is not int or not 1 <= q <= 10:
            raise RuleError("QUANTITY")
        quantities[item["id"]] = quantities.get(item["id"], 0) + q
    for product_id, q in quantities.items():
        if q > 10:
            raise RuleError("QUANTITY")
        if version == "reference" and q > PRODUCTS[product_id]["stock"]:
            raise RuleError("STOCK")
    subtotal = sum(PRODUCTS[k]["price"] * q for k, q in quantities.items())
    eligible = sum(PRODUCTS[k]["price"] * q for k, q in quantities.items() if PRODUCTS[k]["eligible"])
    discount = 0
    if code:
        discount = (eligible + (5 if version == "reference" else 0)) // 10
    after_discount = subtotal - discount
    free = after_discount >= 300000 if version == "reference" else after_discount > 300000
    delivery = 0 if fulfillment == "pickup" or free else 29900
    return {"subtotal": subtotal, "eligible_subtotal": eligible, "discount": discount,
            "after_discount": after_discount, "delivery": delivery, "total": after_discount + delivery}

def sorted_products(version="reference"):
    if version not in ("reference", "candidate"):
        raise RuleError("VERSION")
    key = (lambda p: (p["price"], p["id"])) if version == "reference" else (lambda p: (str(p["price"]), p["id"]))
    return sorted(PRODUCTS.values(), key=key)
