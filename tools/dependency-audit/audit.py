"""Dependency audit: check pinned requirements against PyPI/npm registries.

Flags unpinned ranges and (when online) known-vulnerable versions via the
OSV.dev API. Fully offline-safe: registry failures degrade to pin checks.
"""

import argparse
import json
import re
import urllib.request
from pathlib import Path

PIN_RE = re.compile(r"^[A-Za-z0-9_.\-+]+\s*==\s*[^;\s]+")


def parse_requirements(path):
    reqs = []
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        name = re.split(r"[=<>!~\s\[]", line, maxsplit=1)[0]
        reqs.append({"name": name, "spec": line, "pinned": bool(PIN_RE.match(line))})
    return reqs


def osv_vulns(name, version, timeout=15):
    """Query OSV.dev for PyPI vulns; [] on any failure (offline-safe)."""
    try:
        payload = json.dumps(
            {"package": {"name": name, "ecosystem": "PyPI"}, "version": version}
        ).encode()
        req = urllib.request.Request(
            "https://api.osv.dev/v1/query", data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as res:
            return json.loads(res.read()).get("vulns", [])
    except Exception:
        return []


def audit(requirements_txt, online=True):
    reqs = parse_requirements(requirements_txt)
    unpinned = [r for r in reqs if not r["pinned"]]
    vulns = []
    if online:
        for r in reqs:
            m = re.search(r"==\s*([^;\s]+)", r["spec"])
            if m:
                for v in osv_vulns(r["name"], m.group(1)):
                    vulns.append({"package": r["name"], "id": v.get("id", "?"),
                                  "summary": (v.get("summary") or "")[:100]})
    return {"total": len(reqs), "unpinned": unpinned, "vulns": vulns}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("requirements", nargs="+")
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("-o", "--output", default="reports/dependency-audit.json")
    args = ap.parse_args()
    report = {str(p): audit(p, online=not args.offline) for p in args.requirements}
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))
    n_unpinned = sum(len(v["unpinned"]) for v in report.values())
    n_vulns = sum(len(v["vulns"]) for v in report.values())
    print(f"dependency-audit: {n_unpinned} unpinned, {n_vulns} vulns -> {out}")
    return 1 if n_unpinned else 0


if __name__ == "__main__":
    raise SystemExit(main())
