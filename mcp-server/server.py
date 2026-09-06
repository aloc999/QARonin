"""QARonin QA MCP server: expose quality tooling to coding agents.

Tools (all read-only, repo-root relative):
  tier_report   parse JUnit XMLs + budgets (strategy tier_report.py inputs)
  coverage_gate check coverage.xml against a threshold
  list_suites   enumerate runnable suites + their make targets
  pact_status   consumer/provider pact verification summary

Transport: stdio (MCP). Run: `python mcp-server/server.py` (needs `mcp`).
"""

import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from mcp.server.fastmcp import FastMCP

ROOT = Path(__file__).resolve().parent.parent
mcp = FastMCP("qaronin-qa")

SUITES = {
    "api-python": "make test-tier-api",
    "playwright-ts": "cd frameworks/playwright-ts && npx playwright test",
    "playwright-dotnet": "make csharp-test",
    "cypress": "make cypress-test",
    "bdd": "make bdd-test",
    "karate": "make karate-test",
    "pact": "make pact-test",
}


def _junit_totals(path):
    try:
        root = ET.parse(path).getroot()
    except Exception as e:
        return {"file": path, "error": str(e)[:100]}
    suites = root.findall("testsuite") or ([root] if root.tag == "testsuite" else [])
    t = sum(int(s.attrib.get("tests", 0)) for s in suites)
    bad = sum(int(s.attrib.get("failures", 0)) + int(s.attrib.get("errors", 0)) for s in suites)
    return {"file": path, "tests": t, "failed": bad, "passed": t - bad}


@mcp.tool()
def tier_report(reports: str = "frameworks/playwright-ts/junit.xml,frameworks/api-python/junit.xml") -> str:
    """Summarize JUnit XMLs (comma-separated, repo-root relative)."""
    out = [_junit_totals(str(ROOT / p.strip())) for p in reports.split(",") if p.strip()]
    return json.dumps(out, indent=2)


@mcp.tool()
def coverage_gate(minimum: float = 0.5) -> str:
    """Check coverage.xml line-rate against a threshold."""
    try:
        rate = float(ET.parse(ROOT / "coverage.xml").getroot().attrib.get("line-rate", 0))
    except Exception as e:
        return json.dumps({"ok": False, "error": str(e)[:120]})
    return json.dumps({"ok": rate >= minimum, "line_rate": round(rate, 3), "minimum": minimum})


@mcp.tool()
def list_suites() -> str:
    """List runnable suites and how to run them."""
    return json.dumps(SUITES, indent=2)


@mcp.tool()
def pact_status() -> str:
    """Run the Pact consumer+provider suite and return pass/fail."""
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "contracts/pact/tests", "-q"],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    tail = (r.stdout + r.stderr)[-500:]
    return json.dumps({"ok": r.returncode == 0, "tail": tail})


if __name__ == "__main__":
    mcp.run()
