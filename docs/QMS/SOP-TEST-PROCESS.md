# SOP — Test Process (QMS-SOP-001, v1.0)

Aligned to ISO/IEC/IEEE 29119-2 test process layers.

## 1. Test planning

1. Map the change to tiers (strategy/TEST-STRATEGY.md risk criteria).
2. Update TRACEABILITY-MATRIX.md when requirements change.
3. Confirm the 30-minute regression budget still holds (`make regression-30` dry estimate).

## 2. Test design

1. API-first: new behavior gets api-python + Karate + Pact coverage before UI.
2. UI tests use Page Objects only (no raw selectors in specs), one assertion focus per test.
3. Cross-language parity: TS Playwright cases mirrored in C# (`frameworks/playwright-dotnet`) for smoke/regression tags.
4. External reference: AutomationExercise test_cases 1-26 mapped in `frameworks/automationexercise/README.md`; new e-commerce behavior must cite its AE analogue or record "no analogue".

## 3. Test execution

1. L0 smoke on every PR (< 5 min, blocking).
2. L1 API regression on merge (< 10 min, blocking).
3. Full regression `< 30 min` via `make regression-30` (parallel shards, see docs/REGRESSION-30MIN.md).
4. Live external checks (`AE_LIVE=1`) run nightly only, never as merge gates.

## 4. Reporting & sign-off

1. Generate Visual Report (`make visual-report`) + tier budget report.
2. File defects with: steps, expected/actual, tier, traceability ID, artifact links.
3. Flaky tests follow the quarantine SOP (tag, nightly-only, 10-day time box).
4. Release Manager signs VALIDATION-PLAN.md checklist.

## 5. Nonconformity

Unowned tests, missing traceability links, coverage decline, or regression
over 30 minutes = nonconformity. Record, correct, and preventive-action
within the sprint.
