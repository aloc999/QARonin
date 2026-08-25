#!/usr/bin/env python3
"""Parse JUnit XML files and report per-suite durations against declared budgets."""

import argparse
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SuiteResult:
    name: str
    tests: int
    failures: int
    errors: int
    skipped: int
    time_seconds: float


@dataclass
class TierReport:
    suites: list = field(default_factory=list)

    @property
    def total_tests(self):
        return sum(s.tests for s in self.suites)

    @property
    def total_failures(self):
        return sum(s.failures + s.errors for s in self.suites)

    @property
    def total_time(self):
        return sum(s.time_seconds for s in self.suites)


def parse_junit(path: str) -> TierReport:
    """Parse one JUnit XML file into a TierReport.

    Supports both <testsuites><testsuite> nesting and a bare root <testsuite>.
    """
    tree = ET.parse(path)
    root = tree.getroot()
    report = TierReport()

    if root.tag == "testsuites":
        suite_elems = root.findall("testsuite")
        if not suite_elems:
            aggregate = SuiteResult(
                name=root.get("name") or Path(path).stem,
                tests=int(root.get("tests", 0)),
                failures=int(root.get("failures", 0)),
                errors=int(root.get("errors", 0)),
                skipped=int(root.get("skipped", 0)),
                time_seconds=float(root.get("time", 0)),
            )
            report.suites.append(aggregate)
            return report
    elif root.tag == "testsuite":
        suite_elems = [root]
    else:
        raise ValueError(f"unexpected root element <{root.tag}> in {path}")

    for elem in suite_elems:
        report.suites.append(
            SuiteResult(
                name=elem.get("name") or Path(path).stem,
                tests=int(elem.get("tests", 0)),
                failures=int(elem.get("failures", 0)),
                errors=int(elem.get("errors", 0)),
                skipped=int(elem.get("skipped", 0)),
                time_seconds=float(elem.get("time", 0)),
            )
        )
    return report


def parse_budgets(pairs) -> dict:
    budgets = {}
    for pair in pairs or []:
        if "=" not in pair:
            raise ValueError(f"invalid budget '{pair}', expected suite=seconds")
        key, _, value = pair.partition("=")
        try:
            budgets[key] = float(value)
        except ValueError:
            raise ValueError(f"invalid budget seconds in '{pair}'")
    return budgets


def build_report(paths, budgets) -> str:
    lines = []
    all_reports = []
    for path in paths:
        all_reports.append((path, parse_junit(path)))

    header = f"{'suite':<45} {'tests':>6} {'failed':>7} {'time_s':>9}   status"
    lines.append(header)
    lines.append("-" * len(header))

    over_budget = []
    grand_total_tests = grand_total_failed = grand_total_time = 0.0

    for path, report in all_reports:
        declared = budgets.get(Path(path).stem)
        file_time = report.total_time
        for s in report.suites:
            failed = s.failures + s.errors
            status = "PASS" if failed == 0 else "FAIL"
            lines.append(
                f"{s.name[:44]:<45} {s.tests:>6} {failed:>7} {s.time_seconds:>9.2f}   {status}"
            )
            grand_total_tests += s.tests
            grand_total_failed += failed
        if len(report.suites) > 1:
            lines.append(f"{'  subtotal ' + Path(path).stem:<45} {'':>6} {'':>7} {file_time:>9.2f}")
        grand_total_time += file_time

        if declared is not None and file_time > declared:
            over_budget.append((Path(path).stem, file_time, declared))

    lines.append("-" * len(header))
    lines.append(
        f"{'TOTAL':<45} {grand_total_tests:>6} {grand_total_failed:>7.0f} {grand_total_time:>9.2f}"
    )

    if budgets:
        lines.append("")
        lines.append("Budget check:")
        for stem, spent, limit in sorted(over_budget):
            lines.append(f"  OVER BUDGET  {stem}: {spent:.1f}s > {limit:.0f}s")
        if not over_budget:
            lines.append("  all declared budgets met")

    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="JUnit XML tier duration report")
    parser.add_argument("files", nargs="+", help="JUnit XML files to parse")
    parser.add_argument("--budget", action="append", default=[],
                        metavar="SUITE=SECONDS",
                        help="declared ceiling per junit file stem, e.g. --budget ui=600")
    args = parser.parse_args(argv)

    budgets = parse_budgets(args.budget)
    print(build_report(args.files, budgets))

    exit_code = 0
    parsed = [(p, parse_junit(p)) for p in args.files]
    for path, report in parsed:
        if report.total_failures:
            exit_code = 1
        if Path(path).stem in budgets and report.total_time > budgets[Path(path).stem]:
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
