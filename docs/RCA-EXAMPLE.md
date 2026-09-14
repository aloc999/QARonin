# RCA Example — checkout confirmation timeout (real case, 2026-09-13)

> Scope correction, read first: this repo has **no** `checkout.spec.ts` and
> **no** `/api/payment` endpoint, so the canonical "500 + total mismatch +
> payment-HAR" story cannot be written truthfully here. This RCA uses a real
> failure from CI run `34789667129` instead, with the closest real evidence
> for each lens. Conventions that *would* produce the missing evidence are
> noted as follow-ups.

## Failure

- **Test:** `frameworks/selenium-py/tests/test_regression_cart.py::TestCartRegression::test_checkout_creates_order_confirmation`
- **CI:** `ci` workflow, `selenium-tests` job, branch `qa-hardening-batch`
- **Symptom:** `selenium.common.exceptions.TimeoutException`, `1 failed, 8 passed in 39.70s`
- **Flake proof:** same test passed on the same branch ~30 min earlier
  (run `34788847763`) and the failed job went green on a plain re-run —
  no code change. Intermittent UI timing, not a product regression.

The failing steps (`test_regression_cart.py:40-44`):

```python
cart.open()
cart.checkout()
order_id = cart.order_id_text()   # explicit wait on the confirmation element
assert order_id.startswith("#")
```

## Lens 1 — Logs (CI log, real excerpt)

```text
FAILED tests/test_regression_cart.py::TestCartRegression::test_checkout_creates_order_confirmation
  - selenium.common.exceptions.TimeoutException: Message:
========================= 1 failed, 8 passed in 39.70s =========================
```

`make triage` classifies `TimeoutException` as **`flaky-infra` → owner:
SDET on-call** (see `tools/failure-triage/triage.py` RULES), *not* the BE
team: nothing in the log indicates a server 500 — the 8 passing siblings
prove the target served traffic throughout the run. (This repo has no
JSONL-span error trail for Selenium runs; Playwright runs keep
`trace: on-first-retry` + video/screenshot `retain-on-failure` instead.)

## Lens 2 — DB (order-total reconciliation, real query)

```sql
SELECT id, username, total, status FROM orders ORDER BY id LIMIT 1;
-- (1, 'demo', 85.73, 'confirmed')

SELECT quantity, unit_price FROM order_items WHERE order_id = 1;
-- recomputed total = 49.99 + 15.75 + 19.99 = 85.73 → match=True
```

Stored total equals the recomputed line-item sum: **no total mismatch, no
data corruption**. The order write path (`POST /api/orders` → items →
commit) is exonerated; suspicion stays on the confirmation wait in the
browser. (`db-validation` codifies this check as
`test_api_order_row_matches_line_items`.)

## Lens 3 — Network / visual evidence (gap, stated honestly)

- No HAR is captured for Selenium runs, and `frameworks/selenium-py` has
  **no screenshot-on-failure hook** (verified by grep: zero
  `save_screenshot` calls). There is therefore no frame showing what the
  browser saw at timeout.
- Playwright-side equivalent exists (`trace.zip` + video retained on
  failure) but this failure is in the Selenium suite, so it does not apply.
- **Follow-up (filed, not fixed here):** add a `pytest_runtest_makereport`
  hook in `frameworks/selenium-py` that saves a screenshot + page source on
  failure, mirroring the Playwright artifacts.

## Verdict

| Field | Value |
|-------|-------|
| Owner | SDET on-call (`flaky-infra` bucket) — corrected from "BE team": logs show a client-side wait timeout, DB reconciliation is clean |
| Root cause | Order-confirmation element not ready within the explicit wait on one CI run (timing-sensitive area; cf. commit `e6abdad` "patient order-confirmation wait") |
| Fix | Keep the explicit `WebDriverWait` (no sleeps — `make lint-tests` bans them); re-run green. No quarantine: single occurrence, below the 3-in-14-days bar (`strategy/TEST-STRATEGY.md`) |
| If it recurs | Tag `@flaky-quarantine`, move to nightly non-blocking, extend the confirmation wait or assert on the API-created order first (cf. `docs/MENTORSHIP.md` review checklist) |
