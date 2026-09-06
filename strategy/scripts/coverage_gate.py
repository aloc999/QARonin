"""Coverage gate: fail when total coverage declines below threshold.

Reads coverage.xml (cobertura, as produced by pytest-cov) and compares
line-rate against --min (default 0.70). Prints a one-line summary for the
tier report and exits non-zero on decline.
"""

import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def line_rate(path: Path) -> float:
    tree = ET.parse(path)
    root = tree.getroot()
    rate = root.attrib.get("line-rate")
    if rate is not None:
        return float(rate)
    # Fallback: compute from counters.
    lines_valid = sum(int(c.attrib.get("number", 0)) for c in root.iter("counter") if c.attrib.get("type") == "LINE")
    lines_covered = sum(int(c.attrib.get("covered", 0)) for c in root.iter("counter") if c.attrib.get("type") == "LINE")
    return (lines_covered / lines_valid) if lines_valid else 0.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("coverage_xml", type=Path)
    ap.add_argument("--min", type=float, default=0.70)
    args = ap.parse_args()
    if not args.coverage_xml.exists():
        print(f"coverage gate: {args.coverage_xml} missing -> FAIL")
        return 1
    rate = line_rate(args.coverage_xml)
    status = "PASS" if rate >= args.min else "FAIL"
    print(f"coverage gate: line-rate={rate:.3f} min={args.min:.2f} -> {status}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
