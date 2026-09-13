# Contributing to QARonin

This repo is a multi-framework QA monorepo. Small, deterministic,
well-evidenced PRs beat large ones. This guide covers the two rules that
most often break the build: **how to add a test tier** and **the no-sleep
policy**.

## How to add a new tier (example: L4 soak)

1. **Define it in `strategy/TEST-STRATEGY.md`.** Add a row to the tier table
   (name, budget, CI placement, suites) plus one paragraph under
   "What belongs in each tier, and why". If it has a wall-clock ceiling,
   add it to the budget table too.
2. **Wire the budget mechanically.** `strategy/scripts/tier_report.py` takes
   `--budget <suite>=<seconds>`; `strategy/scripts/regression_30.py` owns the
   30-minute wall clock (`SHARDS` dict). A tier without an enforced budget
   is a suggestion, not a tier — add the shard or the `--budget` flag and a
   CI job that runs it.
3. **Add the CI job.** Mirror an existing job in `.github/workflows/` (and
   `.gitlab-ci.yml` if the tier is release-blocking). Every job must upload
   its JUnit XML as an artifact so `make visual-report` and `make dashboard`
   keep working.
4. **Report it.** `tools/visual-report/generate.py` picks up any `--junit`
   glob automatically; `tools/quality-dashboard/dashboard.py` picks up
   `reports/history/junit-*.xml`. No code change needed — just make sure the
   XML lands in one of those paths.
5. **Document the run command.** Add the `make` target (or `npx`/`pytest`
   one-liner) to the README "Running suites" table and to `make help`.

Checklist before opening the PR:

- [ ] `make lint-tests` passes (no hard waits, no test-module collisions)
- [ ] New JUnit appears in `reports/visual-report.html` locally
- [ ] Tier budget passes via `make tier-report` (or the new `--budget` flag)
- [ ] QMS impact considered (`docs/QMS/` traceability if release-blocking)

## No-sleep policy (enforced)

Fixed sleeps are banned in test code and rejected by `make lint-tests`
(`strategy/scripts/no_hard_waits.py` runs in CI `lint`).

Banned: `waitForTimeout`, `time.sleep`, `Thread.sleep`, `Task.Delay`,
`cy.wait(ms)`, implicit waits (`implicitly_wait`).

Use instead:

| Stack | Do this |
|-------|---------|
| Playwright-TS | auto-retry assertions (`expect(locator).toHaveText`, `toHaveCount`); `retries` is for infra noise only |
| Selenium | `WebDriverWait` via `frameworks/selenium-py/utils/waits.py` |
| Appium | `utils/mobile_wait.py` explicit waits |
| Cypress | `cy.wait(@alias)` on intercepts, never `cy.wait(2000)` |
| API retry under test | backoff helper (see `frameworks/api-python` retry helper, `retry-fetch.ts`) — the sleep is the subject, not a crutch |
| k6 / CI probes | think time and readiness `curl` loops are allowed and documented |

Legitimate exceptions live in `strategy/scripts/no_hard_waits.allowlist`
as `path: reason` lines. Prefer fixing over listing — the allowlist entry
for `test_flaky.py` exists because that file *tests the backoff helper
itself*.

## Other guardrails

- **No new test-module collisions.** Same-basename `test_*.py` across suites
  breaks combined collection; `tools/branch-collision/monitor.py` fails the
  build on anything outside `allowlist.txt`.
- **Coverage must not decline.** `strategy/scripts/coverage_gate.py
  coverage.xml --min 0.8`. If your PR drops the line-rate, add tests —
  do not lower the gate.
- **Meaningful assertions.** Assert behavior (exact texts, counts, shapes,
  status *plus* body, recomputed totals). `assert True` placeholders are
  grep-rejected in review.
- **Visual baselines** (`tests/visual.spec.ts-snapshots/`, chromium only):
  regenerate with `make visual-update` only when the UI intentionally
  changed, and commit the PNG diff together with that UI change.
- **Flaky tests** are defects, not noise: tag confirmed flakes
  `@flaky-quarantine`, remove from blocking tiers within one business day,
  fix or delete within ten working days. See `docs/MENTORSHIP.md` for how
  to review one.
