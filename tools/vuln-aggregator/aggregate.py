"""Vulnerability aggregator: merge pip-audit / npm audit / gitleaks findings
into one Markdown summary for the Visual Report and QMS records.

Inputs are the tools' JSON outputs (all optional; missing = section skipped):
  pip-audit -f json, npm audit --json, gitleaks detect --report-format json.
"""

import argparse
import json
from pathlib import Path


def load_json(path):
    try:
        return json.loads(Path(path).read_text())
    except Exception:
        return None


def summarize_pip_audit(data):
    vulns = (data or {}).get("vulnerabilities", [])
    return [
        {"source": "pip-audit", "package": v.get("package", "?"),
         "id": ",".join(v.get("aliases", v.get("ids", []))[:2]),
         "spec": v.get("spec", ""), "fix": ",".join(v.get("fix_versions", []))}
        for v in vulns
    ]


def summarize_npm_audit(data):
    adv = ((data or {}).get("advisories") or {})
    if adv:
        items = adv.values()
    else:
        items = ((data or {}).get("vulnerabilities") or {}).values()
    return [
        {"source": "npm-audit", "package": a.get("module_name", a.get("name", "?")),
         "id": str(a.get("id", a.get("via", "?")) if not isinstance(a.get("via"), list) else a.get("name")),
         "spec": str(a.get("severity", "")), "fix": str(a.get("fixed_in", a.get("fixAvailable", "")))}
        for a in items
    ]


def summarize_gitleaks(data):
    leaks = data if isinstance(data, list) else []
    return [
        {"source": "gitleaks", "package": l.get("File", "?"),
         "id": l.get("RuleID", "?"), "spec": l.get("Description", "")[:80], "fix": "rotate + revoke"}
        for l in leaks
    ]


def render(findings):
    lines = ["# Vulnerability summary", "", f"Total findings: {len(findings)}", ""]
    lines.append("| Source | Target | ID | Severity/Spec | Fix |")
    lines.append("|---|---|---|---|---|")
    for f in findings:
        lines.append(f"| {f['source']} | {f['package']} | {f['id']} | {f['spec']} | {f['fix']} |")
    if not findings:
        lines.append("| — | no inputs provided (pass audit JSONs) | — | — | — |")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pip", default="pip-audit.json")
    ap.add_argument("--npm", default="npm-audit.json")
    ap.add_argument("--gitleaks", default="gitleaks.json")
    ap.add_argument("-o", "--output", default="reports/vuln-summary.md")
    args = ap.parse_args()
    findings = (
        summarize_pip_audit(load_json(args.pip))
        + summarize_npm_audit(load_json(args.npm))
        + summarize_gitleaks(load_json(args.gitleaks))
    )
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(findings))
    print(f"vuln-aggregator: {len(findings)} findings -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
