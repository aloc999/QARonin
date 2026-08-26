# QARonin vs SDETBMan/qa-automation-portfolio - Gap Analysis

Reference: github.com/SDETBMan/qa-automation-portfolio. This is a factual
comparison of capabilities and design decisions, not a ranking. Their
portfolio is a solid body of work; where QARonin differs, the difference is a
deliberate trade-off, documented below.

## Capability comparison

| Capability | Their approach | QARonin approach | Gap filled |
|------------|----------------|------------------|------------|
| Breadth vs depth | Broad tool coverage (Cypress, Selenium, Playwright, JUnit, Appium embedded in Java suites, JMeter, Gatling) with per-tool sample projects | Fewer tools per capability but each wired end-to-end: one hermetic target, shared page-object contracts, tier budgets, CI gates | Demonstrates integration discipline, not just tool familiarity; every framework runs against a live deterministic app in this repo |
| Mobile/Appium | Embedded inside Java test suites as one more runner | First-class module: gated execution model (`RUN_APPIUM=1`) so the suite is collectable everywhere, unit-tested caps factory and locator tables, dedicated emulator workflow | Shows mobile-specific architecture (capability management, gating strategy), not just Appium API usage |
| Self-healing locators | Healenium plugin attached to Selenium runs | Agentic engine built from scratch: multi-signal offline scoring (attribute/text/structural/positional/uniqueness), optional LLM agent with tool-call round-trip, JSON verdict with rationale, JSONL audit trail, CLI | Explainable healing without external plugins or network dependency; the agent layer is pluggable and auditable |
| Performance testing | JMeter + Gatling scripts | k6 scripts with SLO-as-code thresholds (exit-code gates in CI) + Locust profile with realistic task weighting; both validated against the bundled target | Thresholds act as automated pipeline gates rather than standalone reports; two modern engines compared on the same target |
| System under test | External live sites (heroku-style public demos) -> inherently flaky portfolio: third-party outages break runs | Bundled deterministic FastAPI e-commerce target with seeded data, RBAC, deliberate flaky endpoint for retry demos | Hermetic, reproducible runs; the "flakiness" is intentional and controlled, used to demonstrate retry/backoff engineering |
| Multi-tier time-budget strategy | Not present as an explicit artifact | `strategy/TEST-STRATEGY.md` defines L0-L3 tiers with duration budgets plus a parser that reports actuals vs budget from real JUnit XMLs | Formalized execution economics; budget regressions are visible artifacts, not tribal knowledge |
| SQL validation depth | Basic DB assertions in suites | Dedicated `db-validation` module: order-integrity via SQL aggregation against API-created rows, referential integrity, RBAC-vs-database consistency, seed data quality, snapshot/diff mutation detection | Data-layer claims are proven independently of UI/API layers, catching bugs like inconsistent seeded totals |
| Newman/API chaining | Postman collections present in most portfolios | Postman v2.1 collection with chained auth-token flow through collection variables, response-time budgets, junit output, run alongside pytest API suite in the same gate | Contract coverage across three layers (pytest requests, schema validation, Newman) executed as one pipeline stage |
| Accessibility testing | Not present | axe-core via `@axe-core/playwright` scanning /login, /products, /cart against WCAG 2.1 A/AA; zero critical/serious violations asserted per page; violations dumped to JSON artifacts on failure for triage | NOW COVERED - a11y is a first-class regression gate, not a manual audit |
| Visual regression | Not present | Playwright `toHaveScreenshot()` full-page baselines for login/products/cart at 2% pixel tolerance, chromium baselines committed, `make visual-update` regeneration flow with documented policy | NOW COVERED - UI regressions caught at the pixel level alongside functional suites |
| Flaky-test detection | Not present as a tooling artifact | `tools/flakiness-detector`: stdlib-only Python CLI that classifies tests stable/flaky/broken across repeated JUnit XML runs using flip-rate math, markdown reports, CI gate flags (`--fail-on-flaky`), weekly scheduled scan in ci.yml | NOW COVERED - flakiness is measured and gated, not anecdotal; complements the tier flaky-quarantine policy |
| Security scanning | Not present | `.github/workflows/security.yml`: CodeQL (javascript-typescript + python), pip-audit over every requirements.txt, npm audit --omit=dev on both Node projects with annotation summaries, gitleaks secret scan on full history | NOW COVERED - SAST, dependency auditing and secret detection run on every PR plus weekly schedule |

## What their portfolio has that QARonin currently lacks

Stated honestly, these are real gaps today:

- **Cypress** - a second JS E2E engine; useful for demonstrating intercept/stub ergonomics vs Playwright.
- **Pact contract testing** - provider/consumer contract verification between services; QARonin validates schemas (jsonschema, Postman) but not bi-directional contracts.
- **Terraform / IaC** - environment provisioning as code; QARonin uses docker compose only.
- **DataDog / observability integrations** - correlating test failures with production telemetry.
- **ISO/QMS documentation set** - formal quality-management artifacts beyond TEST-STRATEGY.md.
- **LLM-eval suites** - systematic evaluation harnesses for AI features (QARonin has LLM-based self-healing but no eval framework).
- **C# Playwright** - cross-language Playwright coverage.
- **Karate** - BDD-style API testing in a single DSL.

## Roadmap note

Candidates for phase 3, in rough priority order given the existing
architecture: Pact contracts against the demo target's API (natural fit for
the hermetic service), Karate as a fourth API layer feeding the same tier
budget report, an LLM-eval harness reusing ai-selfhealing's agent plumbing,
and Terraform modules that provision the compose stack for cloud runners.
Cypress and C# Playwright add breadth but overlap existing depth; they are
lower priority unless a role requires them explicitly.
