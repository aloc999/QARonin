# Quality Manual — QARonin (v1.0)

| Field | Value |
|-------|-------|
| Doc ID | QMS-QM-001 |
| Version | 1.0 |
| Status | Approved |
| Owner | QA Lead |
| Approvers | QA Lead, Engineering Manager |
| Review date | Quarterly |
| Standards | ISO 9001:2015 §7-10, ISO/IEC/IEEE 29119-2 |

## 1. Quality policy

We ship releases where every change is covered by a fast, deterministic,
reviewed test tier. A test that is flaky, unowned, or untraceable is a
nonconformity and enters quarantine within one business day.

## 2. Quality objectives (measurable)

1. Full regression completes in **< 30 minutes** (see VALIDATION-PLAN.md).
2. L0+L1 gates green on every merge (100%).
3. Zero blocking tests without an owner and a traceability link.
4. Coverage tracked on every run; decline fails the gate (see coverage gate).
5. Every release ships a Visual Report + tier budget report as quality records.

## 3. Scope

RoninShop demo-target plus all frameworks in this monorepo:
Playwright-TS, Playwright-C# (lintas bahasa parity), Selenium, Appium,
api-python, Karate, Pact, Newman, k6/Locust, db-validation, LLM-eval.

## 4. Roles

| Role | Responsibility |
|------|----------------|
| QA Lead | Owns QMS, approves releases, waives L1 failures with ticket |
| SDET | Owns frameworks, tier budgets, flake quarantine |
| Dev | Fixes product defects, reviews contract changes |
| Release Manager | Signs VALIDATION-PLAN checklist |

## 5. Records

JUnit XML, coverage.xml, visual-report.html, tier budget output, and the
signed validation checklist are retained per release (CI artifacts, 28+ days).
