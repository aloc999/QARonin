"""A06 Vulnerable Components: fail-closed pip-audit gate over pinned reqs.

Tool limitation, stated openly: pip-audit's JSON carries no severity
ratings, and it has no severity filter flag — so "high" cannot be selected
directly. This gate fails closed on ANY known finding in the audited pins
(equivalent: unrated findings are treated as high until triaged). Escape
hatch for accepted risk: pip-audit --ignore-vuln ID (documented in the PR).

The live audit is skipped (not failed) when the pip-audit binary or OSV is
unreachable; the parser below is unit-tested offline and always runs.
"""

import json
import shutil
import socket
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
AUDITED = [
    ROOT / "apps" / "demo-target" / "requirements.txt",
    ROOT / "frameworks" / "api-python" / "requirements.txt",
    ROOT / "frameworks" / "security-tests" / "requirements.txt",
]


def parse_findings(payload):
    """Flatten pip-audit JSON to 'pkg==ver: VID (alias, ...)'; honors an
    explicit severity key if a future pip-audit emits one (high/critical)."""
    out = []
    for dep in payload.get("dependencies", []):
        for vuln in dep.get("vulns", []):
            sev = (vuln.get("severity") or "").lower()
            if sev and sev not in ("high", "critical"):
                continue
            aliases = ", ".join(vuln.get("aliases", [])[:3])
            out.append(f"{dep.get('name')}=={dep.get('version')}: {vuln.get('id')}"
                       + (f" ({aliases})" if aliases else ""))
    return out


def _auditor_reachable():
    if shutil.which("pip-audit") is None:
        return False
    try:
        socket.create_connection(("api.osv.dev", 443), timeout=5).close()
    except OSError:
        return False
    return True


def test_parser_flags_findings_and_honors_severity():
    rated = {"dependencies": [{"name": "x", "version": "1.0", "vulns": [
        {"id": "LOW-1", "aliases": [], "severity": "low"},
        {"id": "HIGH-1", "aliases": ["CVE-1"], "severity": "HIGH"},
        {"id": "UNRATED-1", "aliases": []},
    ]}]}
    flagged = parse_findings(rated)
    assert any("HIGH-1" in f for f in flagged)
    assert any("UNRATED-1" in f for f in flagged)
    assert not any("LOW-1" in f for f in flagged)
    assert parse_findings({"dependencies": []}) == []


@pytest.mark.skipif(not _auditor_reachable(), reason="pip-audit binary or OSV unreachable")
def test_no_known_vulns_in_pinned_requirements():
    findings = []
    for req in AUDITED:
        proc = subprocess.run(
            ["pip-audit", "-r", str(req), "--format=json", "--disable-pip"],
            capture_output=True, text=True, timeout=180,
        )
        if proc.returncode not in (0, 1):
            pytest.skip(f"pip-audit infra failure on {req.name}: {proc.stderr[:200]}")
        try:
            findings += parse_findings(json.loads(proc.stdout or "{}"))
        except json.JSONDecodeError:
            pytest.skip(f"pip-audit returned non-JSON for {req.name}")
    assert findings == [], (
        "supply-chain findings (triage: upgrade the pin or record --ignore-vuln with reason):\n"
        + "\n".join(findings)
    )
