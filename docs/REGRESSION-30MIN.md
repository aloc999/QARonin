# Full Regression in Under 30 Minutes

`make regression-30` runs the whole portfolio in **4 parallel shards** with a
hard **1800s** wall-clock gate (`strategy/scripts/regression_30.py`).

## Shard plan (all parallel)

| Shard | Contents | Typical time |
|-------|----------|--------------|
| A api | demo-target pytest + api-python + Pact + Behave + DeepEval (offline) + Newman | ~3 min |
| B ts-ui | Playwright-TS chromium (smoke+e2e+regression, no @visual) + Cypress E2E | ~10 min |
| C lang-ui | Playwright-C# smoke + Selenium smoke+regression | ~6 min |
| D data | db-validation + observability + selfheal + LLM-eval + AE parity (offline) + MCP + agent + all tools unit tests + collision monitor | ~4 min |

Wall clock: **~6-9 min** typical, budget **30 min**. Firefox full-matrix,
Appium, k6/Locust soak, and live AE checks stay nightly (not in the gate).

## Why it fits

- API/data suites are in-process (TestClient, SQLite) — seconds, not minutes.
- UI is chromium-only in the gate; firefox runs nightly (`ci.yml` matrix).
- Workers: `WORKERS=4 npx playwright test` + pytest `-n auto` where available.
- Live external calls are excluded from the gate (`AE_LIVE=0`).

## Evidence

- `reports/regression-30.md` — per-shard PASS/FAIL + wall time (CI artifact).
- `reports/visual-report.html` — unified dashboard.
- Tier budgets still enforced by `tier_report.py`.
