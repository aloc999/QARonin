"""Claims-diff: snapshot and diff tabular (CSV/JSON) data across runs.

Used for order/catalog reconciliation (e.g. API rows vs DB rows vs yesterday's
snapshot). Exit 0 when identical, 1 with a unified diff otherwise.
"""

import argparse
import csv
import difflib
import json
from pathlib import Path


def load_table(path):
    path = Path(path)
    if path.suffix == ".json":
        rows = json.loads(path.read_text())
        if isinstance(rows, dict):
            rows = [rows]
        return [json.dumps(r, sort_keys=True) for r in rows]
    with open(path, newline="") as f:
        return [",".join(r) for r in csv.reader(f)]


def diff_tables(old_path, new_path):
    old = load_table(old_path)
    new = load_table(new_path)
    return list(difflib.unified_diff(old, new, fromfile=str(old_path), tofile=str(new_path), lineterm=""))


def snapshot_orders_csv(api_base, out_path):
    """Snapshot live order totals (admin) to CSV for tomorrow's diff."""
    import urllib.request

    with urllib.request.urlopen(api_base.rstrip("/") + "/api/admin/orders", timeout=15) as res:
        data = json.loads(res.read())
    lines = ["id,username,status,total"]
    for o in data.get("orders", []):
        lines.append(f"{o['id']},{o['username']},{o['status']},{o['total']}")
    Path(out_path).write_text("\n".join(lines) + "\n")
    return len(lines) - 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("old")
    ap.add_argument("new")
    args = ap.parse_args()
    delta = diff_tables(args.old, args.new)
    if delta:
        print("\n".join(delta))
        print(f"claims-diff: {len(delta)} diff lines -> FAIL")
        return 1
    print("claims-diff: identical -> PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
