# Dependency Audit

Pin hygiene + OSV.dev vulnerability check over `requirements.txt` files.

```bash
python tools/dependency-audit/audit.py apps/demo-target/requirements.txt frameworks/api-python/requirements.txt --offline
python tools/dependency-audit/audit.py apps/demo-target/requirements.txt  # + OSV lookup (needs network)
# or: make dep-audit
python -m pytest tools/dependency-audit/tests -q  # run from tools/dependency-audit
```

Exit 1 when unpinned ranges exist (gate-friendly). Known example: the demo
target pins `starlette<1.0.0` as a range — intentional, documented, and
asserted in the test suite.
