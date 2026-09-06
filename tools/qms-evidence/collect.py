"""QMS evidence collector: bundle release quality records into one pack.

Collects JUnit XMLs, coverage.xml, visual report, tier budgets, vuln summary
and writes reports/qms-evidence/< stamp>/ with a manifest.json mapping every
artifact to ISO 9001:2015 / SOC 2 CC / 29119 clauses. Missing inputs are
recorded as gaps, never fatal.
"""

import argparse
import datetime
import glob
import json
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

CONTROLS = {
    "junit": ["ISO 9001:2015 8.6", "SOC 2 CC7.2", "29119-3 test execution"],
    "coverage": ["ISO 9001:2015 9.1", "SOC 2 CC7.2"],
    "visual-report": ["ISO 9001:2015 7.5", "SOC 2 CC2.1"],
    "tier-budget": ["ISO 9001:2015 8.1", "29119-2 test plan"],
    "vuln-summary": ["ISO 9001:2015 8.5.5", "SOC 2 CC7.1"],
    "validation-plan": ["ISO 9001:2015 8.6", "29119-2 completion"],
}


def junit_summary(path):
    try:
        root = ET.parse(path).getroot()
    except Exception:
        return None
    suites = root.findall("testsuite") or ([root] if root.tag == "testsuite" else [])
    return {
        "tests": sum(int(s.attrib.get("tests", 0)) for s in suites),
        "failures": sum(int(s.attrib.get("failures", 0)) for s in suites),
        "errors": sum(int(s.attrib.get("errors", 0)) for s in suites),
    }


def collect(patterns, dest):
    found = []
    for kind, pattern in patterns.items():
        for src in sorted(set(glob.glob(pattern, recursive=True))):
            target = dest / kind / Path(src).name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(src, target)
            entry = {"kind": kind, "file": str(target.relative_to(dest)),
                     "controls": CONTROLS.get(kind, [])}
            if kind == "junit":
                entry["summary"] = junit_summary(src)
            found.append(entry)
    return found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stamp", default=datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d-%H%M%S"))
    ap.add_argument("-o", "--outdir", default="reports/qms-evidence")
    args = ap.parse_args()
    dest = Path(args.outdir) / args.stamp
    dest.mkdir(parents=True, exist_ok=True)
    patterns = {
        "junit": "**/junit.xml",
        "coverage": "coverage.xml",
        "visual-report": "reports/visual-report.html",
        "vuln-summary": "reports/vuln-summary.md",
        "validation-plan": "docs/QMS/VALIDATION-PLAN.md",
    }
    artifacts = collect(patterns, dest)
    gaps = sorted(set(patterns) - {a["kind"] for a in artifacts})
    manifest = {"stamp": args.stamp, "artifacts": artifacts, "gaps": gaps,
                "controls_index": CONTROLS}
    (dest / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"qms-evidence: {len(artifacts)} artifacts, {len(gaps)} gaps -> {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
