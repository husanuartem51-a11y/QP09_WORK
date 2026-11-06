import argparse, json, sys
from shop_core import quote, sorted_products, RuleError
p=argparse.ArgumentParser()
p.add_argument("--version", choices=["reference", "candidate"], default="reference")
p.add_argument("--input")
p.add_argument("--sort", action="store_true")
a=p.parse_args()
try:
    if a.sort:
        result={"products": sorted_products(a.version)}
    else:
        if not a.input:
            p.error("--input is required unless --sort is used")
        with open(a.input, encoding="utf-8") as f:
            data=json.load(f)
        result=quote(data.get("items"), data.get("promo", ""), data.get("fulfillment", "delivery"), a.version)
    print(json.dumps({"model":"offline-fixture-v1", "version":a.version, "ok":True,"result":result}, ensure_ascii=False, indent=2))
except RuleError as e:
    print(json.dumps({"model":"offline-fixture-v1", "version":a.version,"ok":False,"error":e.code},ensure_ascii=False))
    sys.exit(2)
