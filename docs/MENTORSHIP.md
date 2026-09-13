# Mentorship guide — pairing checklist + reviewing a flaky test

For new SDETs joining QARonin and for seniors reviewing them. Pair on a real
failing suite, not on slides.

## Pairing checklist (30–45 min session)

- [ ] **Reproduce together.** `make target-up`, then the failing command
  (`npx playwright test --grep @smoke`, `pytest -k <name>`, `behave -n …`).
  Confirm the red is real and note the exact error text.
- [ ] **Read the failure, not the code, first.** JUnit message + Playwright
  trace/screenshot/video (`test-results/`) or `reports/failure-triage.json`
  bucket. Classify out loud: `flaky-infra` / `environment` / `assertion` /
  `needs-human` (see `tools/failure-triage/triage.py`).
- [ ] **Check the tier contract.** Which tier (`strategy/TEST-STRATEGY.md`)
  does this test belong in? Would this failure block merge (L0/L1) or just
  report (L2/L3)? Escalation rules apply before debugging depth.
- [ ] **Fix with the mentee driving.** Senior narrates options, mentee types.
  Prefer narrowing the locator/assertion over adding retries.
- [ ] **Prove the fix.** Re-run the single spec, then the tier
  (`make tier-report`). Attach the before/after JUnit to the PR.
- [ ] **Leave a trace.** Update `reports/visual-report.html` /
  `reports/quality-dashboard.html` if the run changes the trend; link the
  Actions run in the PR description.

## How to review a flaky test (step by step)

1. **Confirm intermittence, don't assume it.** Run the spec in isolation
   5× (`--repeat-each=5` in Playwright, `-p no:randomly` + loop in pytest)
   and check `tools/flakiness-detector/` output over `reports/history/`.
   One red in five is flaky; five reds in five is broken.
2. **Bucket it with `make triage`.** `reports/failure-triage.json` maps each
   failure to a bucket + owner + next action:
   - `flaky-infra` (timeout/stale/detached) → SDET on-call, quarantine candidate
   - `environment` (connection/refused/502/target/browser crash) → Platform, check infra first
   - `assertion` (expected-vs-actual) → feature owner, read the diff before touching the test
   - `needs-human` → QA lead, triage manually
3. **Apply the quarantine workflow** (`strategy/TEST-STRATEGY.md` § Flaky-test
   policy): tag `@flaky-quarantine`, remove from blocking tiers within one
   business day, keep running nightly non-blocking. Time-box ten working
   days: fix the test, fix the product bug, or delete with written rationale.
4. **Look for the usual suspects** before approving a retry-based fix:
   - fixed sleep / `waitForTimeout` (banned — see `CONTRIBUTING.md`);
     replace with auto-retry assertions or `WebDriverWait`
   - shared state (SQLite seed, cart, token expiry) — each framework seeds
     its own DB file; check `global-setup.ts` / session fixtures
   - ordering dependence (Newman chained auth, suite-level `beforeAll`) —
     must be explicit, not accidental
   - over-broad locators (`.btn` vs `[data-testid=checkout-submit]`) — the
     `ai-selfhealing` healer log in `reports/healing/*.jsonl` shows which
     renames actually happen in the wild; prefer the stable attribute it
     converges on
5. **Review the evidence, not the story.** A flaky-fix PR must include:
   - the failing JUnit excerpt + triage bucket
   - the isolation re-run count (e.g. "10/10 green after fix")
   - screenshot/trace for UI fixes, or the healed-selector JSONL for
     self-heal fixes
   - confirmation `make lint-tests` still passes (no new sleeps to "stabilize" it)

## Anti-patterns to call out kindly

- Adding `retries: 5` or a sleep to make the red go away.
- Updating visual baselines without inspecting the actual/expected diff.
- Lowering `--min` on the coverage gate instead of adding tests.
- Quarantining forever — the ten-day clock is the kindest thing about the policy.
