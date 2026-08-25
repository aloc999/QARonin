# QARonin

QARonin is a flagship QA engineering portfolio: a monorepo where a realistic
e-commerce system under test ("RoninShop") is exercised by multiple
professional test frameworks, organized under one multi-tier execution
strategy. The name reflects the operating philosophy of the masterless
engineer: no single employer, stack, or tool owns you - you master every
weapon in the QA arsenal and choose the right one for the job.

## Architecture

```
QARonin/
├── apps/
│   └── demo-target/          RoninShop: FastAPI + SQLite + Jinja2 e-commerce app
│                             (JWT-style auth, orders, RBAC, deliberately flaky endpoint)
├── frameworks/
│   ├── playwright-ts/        TypeScript Playwright framework (POM, storageState, tiers)
│   ├── api-python/           pytest + requests API suite with JSON-schema contracts
│   ├── selenium-py/          reserved for phase 2
│   └── appium-mobile/        reserved for phase 2
├── api/
│   └── postman-newman/       Postman v2.1 collection with chained auth + Newman runner
├── strategy/
│   ├── TEST-STRATEGY.md      tier definitions, budgets, flaky policy, pipeline diagram
│   ├── scripts/tier_report.py  JUnit XML duration/budget reporting
│   ├── tests/                unit tests for the reporting logic
│   └── fixtures/             real JUnit XMLs captured from actual runs
├── docker/                   Dockerfiles + compose (target, postgres, test runners)
└── .github/workflows/ci.yml  lint, PR gates, nightly cross-browser regression
```

## Test tiers

| Tier | Name | Budget | Runs in CI | Gate |
|------|------|--------|-----------|------|
| L0 | Smoke | < 5 min | every PR | merge-blocking |
| L1 | API Regression | < 10 min | merge to main | merge-blocking |
| L2 | UI E2E | < 20 min | nightly | report |
| L3 | Full Regression | < 60 min | nightly, release | release sign-off |

Full definitions, escalation rules and the flaky-test quarantine policy are in
[strategy/TEST-STRATEGY.md](strategy/TEST-STRATEGY.md).

## Quickstart

```bash
make install     # python deps, playwright browsers, newman
make ci          # L0+L1 gate: target pytest -> api suite -> smoke -> budget report
```

Individual pieces:

```bash
make target-up                 # start RoninShop on http://127.0.0.1:8199
cd frameworks/playwright-ts && npx playwright test    # UI suites (all browsers)
cd frameworks/api-python && pytest                    # API suite incl. contracts
cd api/postman-newman && npm test                     # Newman collection run
```

## Frameworks

| Directory | Stack | Highlights |
|-----------|-------|------------|
| [frameworks/playwright-ts](frameworks/playwright-ts) | TypeScript, @playwright/test | Page Object Model, storageState global setup via API login, @smoke/@e2e/@regression tags, chromium+firefox projects, junit reporter |
| [frameworks/api-python](frameworks/api-python) | Python, pytest + requests-style client over ASGI | session fixtures, hand-rolled retry helper against /api/flaky, jsonschema contract validation per endpoint |
| [api/postman-newman](api/postman-newman) | Postman Collection v2.1 + Newman | chained login-token flow via collection variables, pm.test assertions, response-time budgets, junit output |
| [apps/demo-target](apps/demo-target) | FastAPI, SQLAlchemy, SQLite | seeded catalog/users/orders, HMAC-signed tokens, admin RBAC, 30%-failure /api/flaky for retry demos |

## Demo credentials

| User | Password | Role |
|------|----------|------|
| demo | demo1234 | user |
| admin | admin1234 | admin |

## Roadmap

Phase 2 modules:

- `frameworks/selenium-py` - Selenium WebDriver parity suite with grid support
- `frameworks/appium-mobile` - mobile automation against a companion app
- `ai-self-healing` - locator self-healing experiments using the flaky endpoint
- `k6` / `locust` - performance tiers (L4) with load profiles per endpoint
- `db-validation` - postgres-backed data-integrity checks using the compose service
