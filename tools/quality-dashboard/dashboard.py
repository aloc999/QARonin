"""Quality dashboard: trend view across collected JUnit runs.

Reads a history dir of junit-*.xml snapshots (written by CI per run) plus the
current coverage line-rate, and renders reports/quality-dashboard.html with
pass-rate trend bars. Single run with no history still renders (trend = today).
"""

import argparse
import glob
import xml.etree.ElementTree as ET
from pathlib import Path


def summarize(path):
    root = ET.parse(path).getroot()
    suites = root.findall("testsuite") or ([root] if root.tag == "testsuite" else [])
    t = sum(int(s.attrib.get("tests", 0)) for s in suites)
    bad = sum(int(s.attrib.get("failures", 0)) + int(s.attrib.get("errors", 0)) for s in suites)
    return {"run": Path(path).stem, "tests": t, "failed": bad,
            "rate": round((t - bad) / t, 3) if t else 0.0}


def render(rows, coverage=None):
    bars = "\n".join(
        f'<div class="row"><span>{r["run"]}</span>'
        f'<div class="bar" style="width:{r["rate"]*100:.0f}%"></div>'
        f'<span>{r["rate"]*100:.0f}% ({r["tests"]-r["failed"]}/{r["tests"]})</span></div>'
        for r in rows
    ) or "<p>No history yet.</p>"
    cov = f"{coverage}" if coverage is not None else "n/a"
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>Quality dashboard</title>
<style>body{{font-family:system-ui;max-width:900px;margin:2rem auto}}.row{{display:flex;gap:.5rem;align-items:center;margin:.25rem 0}}.bar{{background:#16a34a;height:1.2rem}}</style>
</head><body><h1>Quality dashboard</h1><p>Coverage: {cov}</p>{bars}</body></html>"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--history", default="reports/history")
    ap.add_argument("--coverage", default="coverage.xml")
    ap.add_argument("-o", "--output", default="reports/quality-dashboard.html")
    args = ap.parse_args()
    rows = []
    for p in sorted(glob.glob(f"{args.history}/junit-*.xml")):
        try:
            rows.append(summarize(p))
        except Exception:
            continue
    coverage = None
    try:
        coverage = f"{float(ET.parse(args.coverage).getroot().attrib.get('line-rate', 0)) * 100:.1f}%"
    except Exception:
        pass
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(rows[-30:], coverage))
    print(f"quality-dashboard: {len(rows)} historic runs -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
