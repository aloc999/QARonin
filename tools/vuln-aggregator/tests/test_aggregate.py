from aggregate import (
    render,
    summarize_gitleaks,
    summarize_npm_audit,
    summarize_pip_audit,
)


def test_pip_audit_summary():
    data = {"vulnerabilities": [
        {"package": "flask", "aliases": ["CVE-2024-1"], "spec": ">=1,<2", "fix_versions": ["2.0"]}
    ]}
    rows = summarize_pip_audit(data)
    assert rows[0]["package"] == "flask" and "CVE-2024-1" in rows[0]["id"]


def test_pip_audit_empty_and_missing():
    assert summarize_pip_audit(None) == []
    assert summarize_pip_audit({}) == []


def test_npm_audit_summary():
    data = {"advisories": {"1": {"module_name": "lodash", "severity": "high", "id": 1}}}
    rows = summarize_npm_audit(data)
    assert rows[0]["package"] == "lodash"


def test_gitleaks_summary():
    rows = summarize_gitleaks([{"File": "a.py", "RuleID": "generic-api-key", "Description": "x"}])
    assert rows[0]["source"] == "gitleaks" and rows[0]["fix"] == "rotate + revoke"


def test_render_empty_and_full(tmp_path):
    out = render([])
    assert "Total findings: 0" in out
    full = render([{"source": "s", "package": "p", "id": "i", "spec": "x", "fix": "f"}])
    assert "| s | p | i | x | f |" in full
