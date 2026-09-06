"""DataDog reporter: ship JUnit + eval scores as custom metrics/events.

Posts to DataDog v2 API when DD_API_KEY is set; otherwise prints the exact
payload it WOULD send (dry-run, exit 0) so CI without keys still validates
the mapping. Never fails the gate on transport errors.
"""

import argparse
import json
import os
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

SERIES_URL = "https://api.datadoghq.com/api/v2/series"
EVENTS_URL = "https://api.datadoghq.com/api/v1/events"


def junit_metrics(junit_path, tags=()):
    root = ET.parse(junit_path).getroot()
    suites = root.findall("testsuite") or ([root] if root.tag == "testsuite" else [])
    t = sum(int(s.attrib.get("tests", 0)) for s in suites)
    bad = sum(int(s.attrib.get("failures", 0)) + int(s.attrib.get("errors", 0)) for s in suites)
    base = {"tags": [f"suite:{Path(junit_path).stem}", *tags]}
    return [
        {"metric": "qaronin.tests.total", "points": [{"value": t}], **base},
        {"metric": "qaronin.tests.failed", "points": [{"value": bad}], **base},
        {"metric": "qaronin.pass_rate", "points": [{"value": round((t - bad) / t, 4) if t else 0}], **base},
    ]


def post(url, api_key, payload):
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "DD-API-KEY": api_key},
    )
    with urllib.request.urlopen(req, timeout=20) as res:
        return res.status


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--junit", nargs="*", default=[])
    ap.add_argument("--tag", action="append", default=[])
    args = ap.parse_args()
    series = [m for p in args.junit for m in junit_metrics(p, args.tag)]
    key = os.environ.get("DD_API_KEY")
    if not key:
        print(f"datadog-reporter: DRY-RUN {len(series)} series (set DD_API_KEY to ship)")
        print(json.dumps({"series": series}, indent=2)[:2000])
        return 0
    try:
        post(SERIES_URL, key, {"series": series})
        print(f"datadog-reporter: shipped {len(series)} series")
    except Exception as e:
        print(f"datadog-reporter: transport failed, gate unaffected ({e})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
