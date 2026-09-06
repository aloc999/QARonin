# Vulnerability Aggregator

Merges `pip-audit`, `npm audit`, and `gitleaks` JSON outputs into one
Markdown summary (`reports/vuln-summary.md`) for the Visual Report and QMS
records. All inputs optional — missing files render as "no inputs".

```bash
pip-audit -f json -o pip-audit.json --local -r apps/demo-target/requirements.txt || true
npm audit --json > npm-audit.json || true
python tools/vuln-aggregator/aggregate.py --pip pip-audit.json --npm npm-audit.json
# or: make vuln-report
python -m pytest tools/vuln-aggregator/tests -q
```
