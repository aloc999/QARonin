# Validation Plan — Release Sign-off (QMS-VP-001, v1.0)

## Entry criteria

- [ ] L0 smoke green on the release commit
- [ ] L1 API regression green (api-python + Karate + Pact + Newman)
- [ ] Coverage gate passed (no decline vs baseline)
- [ ] Visual Report generated and baselines reviewed

## Validation run (< 30 min)

Run: `make regression-30`. It executes in parallel shards:

1. Shard A: demo-target pytest + api-python + Karate + Pact + Newman (~5 min)
2. Shard B: Playwright-TS chromium smoke+e2e (~8 min)
3. Shard C: Playwright-C# smoke + Selenium smoke (~8 min)
4. Shard D: db-validation + observability + LLM-eval + AE parity (~5 min)

Wall-clock budget: **1800s**. The orchestrator (`strategy/scripts/regression_30.py`)
fails the run if the budget is exceeded. Timing evidence: docs/REGRESSION-30MIN.md.

## Exit criteria

- [ ] All shards green, total wall time < 30 min
- [ ] Tier budget report within ceiling
- [ ] No new flaky-quarantine entries
- [ ] Visual diffs triaged (approve or file defect)

## Sign-off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| QA Lead | | | |
| Release Manager | | | |
