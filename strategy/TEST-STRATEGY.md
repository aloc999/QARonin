# QARonin Multi-Tier Test Strategy

This document defines the execution tiers used across every framework in this
repository. Tiers are the contract between engineering speed and release
confidence: each tier has a declared time budget, a CI placement, and a
defined quality gate. The `strategy/scripts/tier_report.py` tooling enforces
the budgets mechanically.

## Tier definitions

| Tier | Name | Budget | CI placement | Suites |
|------|------|--------|--------------|--------|
| L0 | Smoke | < 5 min | PR gate (blocking) | playwright `@smoke`, demo-target pytest, api-python `smoke` marker |
| L1 | API Regression | < 10 min | Merge gate (blocking) | api-python full suite (incl. contracts), Newman collection, demo-target pytest |
| L2 | UI E2E | < 20 min | Nightly + pre-release | playwright `@e2e` + `@regression` (chromium) |
| L3 | Full Regression | < 60 min | Nightly + release sign-off | all of L2 plus cross-browser matrix (chromium + firefox), contract suite, dockerized runs |

### What belongs in each tier, and why

- **L0 Smoke** answers one question: is the build fundamentally broken?
  Login, product grid rendering, order creation happy path. Anything slower
  than a few seconds per test does not belong here. Fast feedback is the
  entire value; coverage is not.
- **L1 API Regression** carries most functional coverage. API tests are cheap,
  stable, and locate failures precisely. Schema/contract tests live here so
  that interface drift is caught before any UI test sees it.
- **L2 UI E2E** validates user-visible journeys end to end: purchase flow,
  cart persistence, RBAC surfaced through the browser. Kept small because UI
  suites are the slowest and flakiest investment.
- **L3 Full Regression** is L2 plus cross-browser sharding and everything
  else. It exists for release confidence, not development feedback.

### Execution-time budget table

| Suite | Declared budget (seconds) | Enforced by |
|-------|---------------------------|-------------|
| demo-target pytest | 60 | tier_report.py --budget target=60 |
| api-python | 300 | tier_report.py --budget api=300 |
| postman-newman | 120 | tier_report.py --budget newman=120 |
| playwright-ts (all projects) | 600 | tier_report.py --budget ui=600 |

Budgets are ceilings, not targets. A suite trending toward its ceiling in the
tier report is a refactoring signal.

### Risk-based selection criteria

When time-constrained (hotfix, partial merge), select tests by:

1. **Changed-surface mapping**: modules touched since last green build map to
   suites via directory convention (`apps/demo-target/app/*` -> L1; UI pages
   touched -> relevant page-object specs).
2. **Failure history**: suites with recent flakes or escapes run first.
3. **Business criticality**: auth, orders, and checkout paths outrank content
   pages.
4. **Cost asymmetry**: prefer tests whose failure cost exceeds their runtime.

### Escalation rules

- Any L0 failure blocks merge; no triage discussion.
- L1 failure blocks merge unless explicitly waived by an owner with a linked
  ticket.
- Two consecutive nightly L2/L3 failures promote the failing spec into L1
  until fixed.
- Any test that fails intermittently three times in fourteen days enters the
  quarantine workflow below.

## Parallelization and sharding plan

- api-python and demo-target pytest are single-process today (< 1s combined);
  parallelization would add overhead without benefit.
- playwright-ts shards by worker count (`WORKERS` env var). Cross-browser
  sharding happens at the project level: chromium and firefox run as separate
  projects and can be split across CI runners via `--shard`.
- Newman runs single-iteration by design: the chained token flow depends on
  request ordering.
- Target-level isolation: every framework seeds its own SQLite file so suites
  can run concurrently against separate server instances if needed.

## Quality gates per tier

| Gate | Condition |
|------|-----------|
| L0 pass | 100% smoke tests green |
| L1 pass | 100% API regression green, zero quarantined tests executed as blocking |
| L2 pass | 100% e2e green on chromium; retries allowed but reported |
| L3 pass | 100% green on all browsers; tier report within budget |

## Flaky-test policy

Flakiness is treated as a defect in the test or the system under test, never
as background noise.

1. **Detection**: retry counts from Playwright reports and intermittent CI
   failures feed the flake log.
2. **Quarantine workflow**: a confirmed flaky test is tagged `@flaky-quarantine`
   and removed from blocking tiers within one business day. It still executes
   nightly, non-blocking.
3. **Time box**: quarantine expires after ten working days. Fix the test, fix
   the product bug, or delete the test with a written rationale.
4. **Retry discipline**: Playwright `retries` exist to absorb infrastructure
   noise, not product bugs. A test that only passes on retry is already in
   violation and enters quarantine automatically.

The `/api/flaky` endpoint in the demo target exists specifically to exercise
this policy: retry helpers must absorb its 503s inside the test body so the
suite itself stays deterministic.

## Pipeline diagram

```
 pull request                merge to main                    nightly (cron)
 ────────────               ──────────────                   ──────────────
 ┌─────────────────┐        ┌────────────────────┐          ┌──────────────────────────┐
 │ lint            │        │ target-tests       │          │ nightly-regression       │
 │                 │        │   pytest (21)      │          │                          │
 │ target-tests    │        │                    │          │  L2: playwright @e2e     │
 │   pytest (21)   │        │ api-tests          │          │      + @regression       │
 │                 │        │   pytest (33)      │          │                          │
 │ api-tests (L0)  │        │   incl. contracts  │          │  L3: cross-browser matrix│
 │                 │        │                    │          │   [chromium] [firefox]   │
 │ playwright-smoke│        │ postman-newman     │          │                          │
 │   @smoke (L0)   │        │   collection (24)  │          │  tier_report.py budget   │
 │                 │        │         (L1)       │          │   check on all junit.xml │
 │ tier_report.py  │        │                    │          │                          │
 │   budget check  │        │ tier_report.py     │          └──────────────────────────┘
 └─────────────────┘        └────────────────────┘
        block                     block                        report + alert
```

## Reporting

Every CI job writes JUnit XML. `make tier-report` parses all reports and
prints a per-suite duration table, flagging any suite over its declared
budget. Sample outputs produced from real runs live in
`strategy/fixtures/`.
