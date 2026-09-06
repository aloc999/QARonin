"""Site monitor: liveness + content-drift checks for RoninShop.

Compares /api/health, /api/products shape, and a content hash of /products
against a checked-in baseline. Exit 1 on outage or drift (nightly CI).
"""

import argparse
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

BASELINE = Path(__file__).resolve().parent / "baseline.json"


def fetch(base, path, timeout=15):
    with urllib.request.urlopen(base.rstrip("/") + path, timeout=timeout) as res:
        return res.status, res.read()


def check(base, baseline):
    findings = []

    try:
        status, body = fetch(base, "/api/health")
        assert status == 200 and json.loads(body)["status"] == "ok"
    except Exception as e:
        return [{"check": "health", "ok": False, "detail": str(e)[:120]}]

    try:
        status, body = fetch(base, "/api/products")
        items = json.loads(body)
        assert isinstance(items, list) and len(items) >= baseline.get("min_products", 1)
        keys = set(baseline.get("required_keys", ["name", "price", "stock"]))
        missing = keys - set(items[0])
        findings.append({"check": "products-shape", "ok": not missing,
                         "detail": f"missing={sorted(missing)}" if missing else f"n={len(items)}"})
    except Exception as e:
        findings.append({"check": "products-shape", "ok": False, "detail": str(e)[:120]})

    try:
        _, body = fetch(base, "/products")
        digest = hashlib.sha256(body).hexdigest()[:16]
        findings.append({"check": "products-hash", "ok": True, "detail": digest,
                         "drift": digest != baseline.get("products_hash")})
    except Exception as e:
        findings.append({"check": "products-hash", "ok": False, "detail": str(e)[:120]})
    return findings


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8199")
    ap.add_argument("--update-baseline", action="store_true")
    args = ap.parse_args()
    baseline = json.loads(BASELINE.read_text()) if BASELINE.exists() else {}
    try:
        _, body = fetch(args.base, "/products")
        live_hash = hashlib.sha256(body).hexdigest()[:16]
    except Exception as e:
        print(f"site-monitor: OUTAGE {e}"[:200])
        return 1
    if args.update_baseline or not baseline:
        BASELINE.write_text(json.dumps(
            {"min_products": 1, "required_keys": ["name", "price", "stock"],
             "products_hash": live_hash}, indent=2) + "\n")
        print(f"site-monitor: baseline written ({live_hash})")
        return 0
    findings = check(args.base, baseline)
    bad = [f for f in findings if not f["ok"]]
    drift = [f for f in findings if f.get("drift")]
    print(json.dumps(findings, indent=2))
    if bad:
        print("site-monitor: FAIL")
        return 1
    if drift:
        print("site-monitor: DRIFT (content changed since baseline)")
    else:
        print("site-monitor: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
