"""No-hard-waits gate: fail when test code uses fixed sleeps.

Scans test/spec sources for banned patterns. Conditional waits (explicit
WebDriverWait, Playwright auto-retry assertions, cy.wait(@alias), retry with
backoff, k6 think time, CI readiness probes) are the blessed alternatives
and are NOT flagged. Documented exceptions live in allowlist.txt with reasons.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

# pattern -> (message, applicable extensions note)
BANNED = [
    (re.compile(r"waitForTimeout\s*\("), "fixed Playwright timeout; use auto-retry assertions"),
    (re.compile(r"time\.sleep\s*\("), "fixed sleep; use explicit waits or backoff helpers"),
    (re.compile(r"Thread\.sleep\s*\("), "fixed sleep; use explicit waits"),
    (re.compile(r"Task\.Delay\s*\("), "fixed delay; use Playwright assertions"),
    (re.compile(r"cy\.wait\s*\(\s*\d"), "fixed cy.wait(ms); wait on aliases/intercepts instead"),
    (re.compile(r"implicitly_wait\s*\("), "implicit waits; use explicit WebDriverWait"),
]

SCAN_DIRS = [
    "frameworks/playwright-ts/tests", "frameworks/playwright-ts/pages",
    "frameworks/playwright-dotnet/Tests", "frameworks/playwright-dotnet/Pages",
    "frameworks/selenium-py", "frameworks/appium-mobile",
    "frameworks/cypress/cypress", "frameworks/bdd-python/features",
    "frameworks/api-python/tests", "frameworks/automationexercise/tests",
    "apps/demo-target/tests", "contracts/pact/tests",
    "evals/llm/tests", "evals/deepeval",
]

ALLOWLIST = Path(__file__).resolve().parent / "no_hard_waits.allowlist"


def load_allowlist():
    """File-level exceptions: {relative path: reason}."""
    if not ALLOWLIST.exists():
        return {}
    entries = {}
    for line in ALLOWLIST.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and ":" in line:
            path, _, reason = line.partition(":")
            entries[path.strip()] = reason.strip()
    return entries


def scan():
    allowed = load_allowlist()
    violations = []
    for d in SCAN_DIRS:
        for path in sorted((ROOT / d).rglob("*")):
            if not path.is_file() or path.suffix not in (".ts", ".js", ".jsx", ".py", ".cs", ".java"):
                continue
            if "__pycache__" in path.parts or "node_modules" in path.parts:
                continue
            rel = str(path.relative_to(ROOT))
            text = path.read_text(errors="replace")
            for rx, msg in BANNED:
                for i, line in enumerate(text.splitlines(), 1):
                    if rx.search(line) and rel not in allowed:
                        violations.append(f"{rel}:{i}: {msg}\n    {line.strip()[:120]}")
    return violations


def main() -> int:
    violations = scan()
    if violations:
        print(f"no-hard-waits: {len(violations)} violation(s):")
        print("\n".join(violations))
        print("Fix with explicit waits, or document in strategy/scripts/no_hard_waits.allowlist")
        return 1
    print("no-hard-waits: clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
