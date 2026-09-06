"""Failure triage: classify JUnit failures into cause buckets with owners.

Heuristic (no LLM key needed): timeout/async words -> flaky-infra; assertion
mismatch -> product-or-test; connection/refused -> environment; everything
else -> needs-human. An optional ANTHROPIC_API_KEY path re-words the summary
(same buckets, skipped offline).
"""

import argparse
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

RULES = [
    ("flaky-infra", re.compile(r"timeout|wait|retry|flaky|stale|detached|animationframe", re.I),
     "SDET on-call", "quarantine candidate: rerun in isolation, then apply flake policy"),
    ("environment", re.compile(r"connection|refused|econn|dns|502|503|target|docker|browser.*(crash|closed)|executable", re.I),
     "Platform", "check target/browser infra before blaming the test"),
    ("assertion", re.compile(r"assert|expect|equal|match|snapshot|tohave|toequal|visible|enabled", re.I),
     "Feature owner", "read expected-vs-actual; update test or file product bug"),
]


def classify(text):
    for bucket, rx, owner, advice in RULES:
        if rx.search(text or ""):
            return bucket, owner, advice
    return "needs-human", "QA lead", "no rule matched; triage manually"


def triage(junit_path):
    root = ET.parse(junit_path).getroot()
    cases = root.iter("testcase") if root.tag != "testsuite" else root.iter("testcase")
    out = []
    for tc in root.iter("testcase"):
        fail = tc.find("failure")
        err = tc.find("error")
        node = fail if fail is not None else err
        if node is None:
            continue
        text = f"{node.attrib.get('message', '')}\n{node.text or ''}"
        bucket, owner, advice = classify(text)
        out.append({"test": f"{tc.attrib.get('classname', '')}::{tc.attrib.get('name', '')}",
                    "bucket": bucket, "owner": owner, "advice": advice,
                    "excerpt": text.strip()[:200]})
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("junit", nargs="+")
    ap.add_argument("-o", "--output", default="reports/failure-triage.json")
    args = ap.parse_args()
    results = [t for p in args.junit for t in triage(p)]
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2))
    buckets = {}
    for r in results:
        buckets[r["bucket"]] = buckets.get(r["bucket"], 0) + 1
    print(f"failure-triage: {len(results)} failures {buckets} -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
