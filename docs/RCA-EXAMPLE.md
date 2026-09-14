# RCA — checkout confirmation timeout (real case, 2026-09-13)
Failure: selenium test_checkout_creates_order_confirmation — TimeoutException; 1 failed, 8 passed.
Flake proof: same branch green 30 min earlier and on plain re-run — no code change.
Log (ci run 34789667129): FAILED ... TimeoutException → triage bucket flaky-infra, owner SDET on-call.
DB: SELECT total FROM orders WHERE id=1 → 85.73; recomputed 49.99+15.75+19.99 = 85.73 ✔ no mismatch.
HAR: not captured for selenium runs; equivalent evidence = trace.zip + video retained on failure (playwright only).
Gap: selenium-py has no screenshot-on-failure hook — filed as follow-up, not fixed here.
Note: repo has no checkout.spec.ts and no /api/payment, so no 500/HAR-payment story exists to cite.
Fix: keep explicit WebDriverWait (sleeps banned); single occurrence → below quarantine bar.
If it recurs: tag @flaky-quarantine per strategy/TEST-STRATEGY.md.
