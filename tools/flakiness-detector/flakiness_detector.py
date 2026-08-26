#!/usr/bin/env python3
"""Flakiness detector: classify tests across repeated JUnit XML runs.

Reads N JUnit XML files (from repeated CI runs), builds per-test outcome
history, and classifies each test as:

- stable:  never failed across all runs
- broken:  never passed across all runs
- flaky:   outcome flipped at least once (flip-rate = flips / transitions)

Stdlib only.
"""

from __future__ import annotations

import argparse
import glob
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path


def parse_junit(path: str) -> dict[str, bool]:
    """Return {test_id: passed_bool} for one junit XML file.

    test_id is "classname::name" when classname exists, else "name".
    """
    outcomes: dict[str, bool] = {}
    root = ET.parse(path).getroot()
    for case in root.iter("testcase"):
        name = case.get("name", "<unknown>")
        classname = case.get("classname", "")
        test_id = f"{classname}::{name}" if classname else name
        failed = case.find("failure") is not None or case.find("error") is not None
        skipped = case.find("skipped") is not None
        if skipped:
            continue  # skips carry no signal; omit from history
        outcomes[test_id] = not failed
    return outcomes


def load_histories(paths: list[str]) -> tuple[dict[str, list[bool]], list[str]]:
    """Load run files in the given order; return ({test_id: [bool per run]}, [run labels])."""
    histories: dict[str, list[bool]] = defaultdict(list)
    labels: list[str] = []
    ordered: dict[str, list[bool]] = {}
    for path in paths:
        labels.append(path)
        outcomes = parse_junit(path)
        for test_id, passed in outcomes.items():
            histories.setdefault(test_id, []).append(passed)
    # preserve deterministic ordering
    for k in sorted(histories):
        ordered[k] = histories[k]
    return ordered, labels


def count_flips(history: list[bool]) -> int:
    """Number of times the outcome changed between consecutive runs."""
    return sum(1 for a, b in zip(history, history[1:]) if a != b)


def classify(
    history: list[bool], min_runs: int = 2
) -> tuple[str, float | None]:
    """Classify one test.

    Returns (status, flip_rate) where flip_rate = flips / transitions,
    or (status, None) when there are no transitions (stable/broken).
    """
    if len(history) < min_runs:
        return "insufficient-data", None
    if all(history):
        return "stable", None
    if not any(history):
        return "broken", 0.0
    transitions = len(history) - 1
    if transitions == 0:
        # single-run mix impossible; guarded by all/any above
        return "stable" if history[0] else "broken", None
    flips = count_flips(history)
    if flips == 0:
        # e.g. [F, F, T]: never flipped between runs but mixed overall;
        # treat a permanent regime change as flaky with full flip rate
        return "flaky", 1.0
    return "flaky", flips / transitions


def build_report(
    histories: dict[str, list[bool]], min_runs: int
) -> tuple[str, dict[str, int]]:
    """Build markdown report; return (markdown, summary counts)."""
    rows = []
    counts = {"stable": 0, "flaky": 0, "broken": 0, "insufficient-data": 0}
    for test_id in sorted(histories):
        history = histories[test_id]
        status, flip_rate = classify(history, min_runs)
        counts[status] += 1
        marks = "".join("P" if p else "F" for p in history)
        rate = f"{flip_rate:.2f}" if flip_rate is not None else "-"
        rows.append((test_id, status, rate, len(history), marks))

    lines = ["# Flakiness report", ""]
    lines.append(
        f"Runs analyzed: {max(len(h) for h in histories.values()) if histories else 0}"
    )
    lines.append("")
    lines.append("| Test | Status | Flip rate | Runs seen | History |")
    lines.append("|------|--------|-----------|-----------|---------|")
    for test_id, status, rate, runs, marks in rows:
        lines.append(f"| `{test_id}` | {status} | {rate} | {runs} | {marks} |")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- stable: {counts['stable']}")
    lines.append(f"- flaky: {counts['flaky']}")
    lines.append(f"- broken: {counts['broken']}")
    if counts["insufficient-data"]:
        lines.append(f"- insufficient-data: {counts['insufficient-data']}")
    lines.append("")
    return "\n".join(lines), counts


def expand_paths(patterns: list[str]) -> list[str]:
    """Expand globs/dirs into an ordered, deduplicated file list."""
    files: list[str] = []
    for pattern in patterns:
        matched = sorted(glob.glob(pattern))
        if not matched:
            p = Path(pattern)
            if p.is_dir():
                matched = sorted(str(x) for x in p.glob("**/*.xml"))
            else:
                raise SystemExit(f"error: no files match '{pattern}'")
        for m in matched:
            if m not in files:
                files.append(m)
    if not files:
        raise SystemExit("error: no junit XML files provided")
    return files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="flakiness-detector",
        description="Detect flaky/broken/stable tests across repeated JUnit XML runs.",
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        help="JUnit XML files, glob patterns, or directories",
    )
    parser.add_argument("--min-runs", type=int, default=2,
                        help="minimum runs before classifying (default: 2)")
    parser.add_argument("--fail-on-flaky", action="store_true",
                        help="exit 1 if any test is classified flaky")
    parser.add_argument("--fail-on-broken", action="store_true",
                        help="exit 1 if any test is classified broken")
    parser.add_argument("-o", "--output", default=None,
                        help="write markdown report to file instead of stdout")
    args = parser.parse_args(argv)

    files = expand_paths(args.inputs)
    histories, _labels = load_histories(files)
    report, counts = build_report(histories, args.min_runs)

    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"report written to {args.output}")
    else:
        print(report)

    if args.fail_on_broken and counts["broken"] > 0:
        print(f"FAIL: {counts['broken']} broken test(s)", file=sys.stderr)
        return 1
    if args.fail_on_flaky and counts["flaky"] > 0:
        print(f"FAIL: {counts['flaky']} flaky test(s)", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
