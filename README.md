# QARonin

![ci](https://github.com/aloc999/QARonin/actions/workflows/ci.yml/badge.svg)
![mobile](https://github.com/aloc999/QARonin/actions/workflows/mobile.yml/badge.svg)
![security](https://github.com/aloc999/QARonin/actions/workflows/security.yml/badge.svg)

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
│                             (JWT-style auth, orders, RBAC, /api/health, /metrics,
│                              deliberately flaky endpoint)
├── frameworks/
│   ├── playwright-ts/        TypeScript Playwright framework (POM, storageState, tiers,
│   │                         incl. ae-parity.spec.ts vs AutomationExercise cases)
│   ├── playwright-dotnet/    C# Playwright lintas-bahasa parity (same smoke/regression tags)
│   ├── api-python/           pytest + requests API suite with JSON-schema contracts
│   ├── selenium-py/          Selenium 4 + pytest suite (chrome/firefox/grid, same POM)
│   ├── appium-mobile/        Appium 2 + UiAutomator2 skeleton (emulator-gated)
│   ├── karate/               Karate DSL API layer (auth/products/orders, JUnit via Maven)
│   └── automationexercise/   Live + parity suite vs automationexercise.com/test_cases (26 cases)
├── contracts/pact/           Pact consumer-driven contracts + provider verification
├── ai-selfhealing/           Agentic self-healing locator engine (offline heuristics
│                             + optional LLM agent, CLI, JSONL audit trail)
├── evals/llm/                LLM-eval harness scoring the healer (accuracy/latency JSON)
├── perf/
│   ├── k6/                   SLO-as-code load scripts (checkout, API, smoke)
│   └── locust/               Weighted-task Locust profile with custom CSV stats
├── db-validation/            SQL data-validation framework (order integrity,
│                             referential checks, RBAC-vs-DB, snapshots/diffs)
├── api/
│   └── postman-newman/       Postman v2.1 collection with chained auth + Newman runner
├── infra/terraform/          Terraform IaC for ephemeral QA envs (validate/plan in CI)
├── observability/            /metrics + structured logs + Prometheus/OTel configs + dashboard
├── tools/
│   ├── flakiness-detector/   Stdlib-only Python CLI: classifies tests
│   │                         stable/flaky/broken across repeated junit runs
│   └── visual-report/        Stdlib HTML dashboard: junit + coverage + LLM-eval
├── docs/
│   ├── QMS/                  ISO 9001 / 29119 QMS pack (manual, SOP, traceability, validation plan)
│   └── REGRESSION-30MIN.md   4-shard sub-30-minute gate design + timing evidence
├── strategy/
│   ├── TEST-STRATEGY.md      tier definitions, budgets, flaky policy, pipeline diagram
│   ├── scripts/tier_report.py  JUnit XML duration/budget reporting
│   ├── scripts/regression_30.py  parallel 30-min orchestrator + gate
│   ├── scripts/coverage_gate.py  coverage decline gate
│   ├── tests/                unit tests for the reporting logic
│   └── fixtures/             real JUnit XMLs captured from actual runs
├── docs/COMPARISON.md        gap analysis vs reference QA portfolios
├── docker/                   Dockerfiles + compose (target, postgres, test runners)
├── .github/workflows/        ci.yml, regression-30min.yml (parallel 30-min gate),
│                             mobile.yml, security.yml
└── .gitlab-ci.yml            GitLab mirror pipeline (same 30-min gate)
```

## Test tiers

| Tier | Name | Budget | Runs in CI | Gate |
|------|------|--------|-----------|------|
| L0 | Smoke | < 5 min | every PR | merge-blocking |
| L1 | API Regression | < 10 min | merge to main | merge-blocking |
| L2 | UI E2E | < 20 min | nightly | report |
| L3 | Full Regression | < 30 min | nightly, release | release sign-off (`make regression-30`, 4 parallel shards) |

Full definitions, escalation rules and the flaky-test quarantine policy are in
[strategy/TEST-STRATEGY.md](strategy/TEST-STRATEGY.md).

## Quickstart

```bash
make install     # python deps, playwright browsers, newman
make ci          # L0+L1 gate: target pytest -> api suite -> smoke -> budget report
make regression-30  # full gate: 4 parallel shards, hard 30-min budget
```

Individual pieces:

```bash
make target-up                 # start RoninShop on http://127.0.0.1:8199
cd frameworks/playwright-ts && npx playwright test    # UI suites (all browsers)
cd frameworks/api-python && pytest                    # API suite incl. contracts
cd api/postman-newman && npm test                     # Newman collection run

make selenium-test             # Selenium 4 suite (smoke + regression markers)
make pact-test                 # Pact consumer + provider contracts (L1)
make karate-test               # Karate DSL suite vs live target (needs mvn)
make csharp-test               # Playwright .NET lintas-bahasa smoke (needs dotnet)
make tf-validate               # Terraform init + validate (skips if missing)
make obs-test                  # observability (/health, /metrics, logs)
make llm-eval                  # LLM-eval harness + pytest
make ae-test                   # AutomationExercise parity, offline (AE_LIVE=0)
make coverage                  # pytest-cov across python suites + decline gate
make visual-report             # unified HTML dashboard -> reports/visual-report.html
make regression-30             # full 4-shard gate, fails if wall > 30 min
make selfheal-test             # self-healing engine tests + offline CLI demo
make perf-smoke                # k6 smoke script + 20s Locust headless run
make db-validate               # DB validation vs the live demo target's SQLite
make appium-collect            # mobile suite collection (skips without RUN_APPIUM=1)
make visual-update             # regenerate Playwright visual baselines (chromium)
make flake-check               # flakiness-detector report over bundled fixtures
python -m selfheal heal \      # self-healing CLI (offline heuristic mode)
  --failure ai-selfhealing/fixtures/sample_failure.json \
  --dom ai-selfhealing/fixtures/sample_dom.json
```

## Frameworks

| Directory | Stack | Highlights |
|-----------|-------|------------|
| [frameworks/playwright-ts](frameworks/playwright-ts) | TypeScript, @playwright/test | Page Object Model, storageState global setup via API login, @smoke/@e2e/@regression tags, chromium+firefox projects, junit reporter, axe-core accessibility scans (@a11y, WCAG 2.1 AA gate with JSON triage artifacts), full-page visual regression via toHaveScreenshot (@visual, 2% tolerance) |
| [frameworks/api-python](frameworks/api-python) | Python, pytest + requests-style client over ASGI | session fixtures, hand-rolled retry helper against /api/flaky, jsonschema contract validation per endpoint |
| [contracts/pact](contracts/pact) | Python, Pact v2 (broker-free) | consumer contract JSON + TestClient provider verification, L1 gate |
| [frameworks/karate](frameworks/karate) | Java 17, Karate 1.4 + JUnit5 | auth/products/orders DSL features feeding tier budgets |
| [frameworks/playwright-dotnet](frameworks/playwright-dotnet) | C#, Playwright 1.40 + NUnit (.NET 6) | lintas-bahasa parity: same @smoke/@regression tags as TS |
| [frameworks/automationexercise](frameworks/automationexercise) | Python, pytest + requests | live reference checks (cases 1-26) + offline RoninShop parity |
| [evals/llm](evals/llm) | Python | fixed JSONL healer dataset, accuracy/latency gate, eval-report.json |
| [infra/terraform](infra/terraform) | Terraform >= 1.6 | ephemeral QA env manifest, credential-free validate/plan in CI |
| [observability](observability) | Python stdlib + FastAPI | /api/health, /metrics (Prometheus), JSONL spans, OTel/Prom configs, Grafana dashboard |
| [tools/visual-report](tools/visual-report) | Python stdlib | one HTML dashboard from junit + coverage + LLM-eval |
| [docs/QMS](docs/QMS) | Markdown | ISO 9001/29119 QMS: manual, SOP, traceability, validation plan, doc control |
| [api/postman-newman](api/postman-newman) | Postman Collection v2.1 + Newman | chained login-token flow via collection variables, pm.test assertions, response-time budgets, junit output |
| [apps/demo-target](apps/demo-target) | FastAPI, SQLAlchemy, SQLite | seeded catalog/users/orders, HMAC-signed tokens, admin RBAC, 30%-failure /api/flaky for retry demos |
| [frameworks/selenium-py](frameworks/selenium-py) | Python, Selenium 4 + pytest | same POM contract as playwright-ts, explicit-wait wrapper (no sleeps), chrome/firefox headless via Selenium Manager, Grid via SELENIUM_REMOTE_URL, @smoke/@regression markers |
| [ai-selfhealing](ai-selfhealing/README.md) | Python, requests (LLM optional) | multi-signal offline locator scoring, pluggable OpenAI-compatible agent with graceful fallback, ranked candidates + confidence + rationale, JSONL healing report, CLI |
| [perf/k6](perf/k6/README.md) | k6 (JS) | SLO-as-code thresholds as CI gates (p95<800ms reads, p95<1200ms orders, <1% errors), staged ramp profiles |
| [perf/locust](perf/locust/README.md) | Locust (Python) | weighted tasks (60% browse / 25% cart / 10% login / 5% order), 1-3s think time, custom stats CSV listeners |
| [db-validation](db-validation) | Python, SQLAlchemy 2.x + pytest | order integrity via SQL aggregation vs API-created rows, orphan-FK checks, RBAC-vs-database consistency, seed quality rules, snapshot/diff mutation detection |
| [frameworks/appium-mobile](frameworks/appium-mobile/README.md) | Python, Appium 2 + UiAutomator2 | emulator-gated suite (RUN_APPIUM=1 else clean skips), caps factory, wdio native demo app flows, dedicated emulator workflow |
| [tools/flakiness-detector](tools/flakiness-detector/README.md) | Python (stdlib only) | classifies tests stable/flaky/broken across repeated JUnit XML runs via flip-rate math, markdown reports, --fail-on-flaky/--fail-on-broken CI gates, bundled synthetic fixtures + pytest suite, weekly scheduled scan in ci.yml |
| [.github/workflows/security.yml](.github/workflows/security.yml) | GitHub Actions | CodeQL (javascript-typescript + python), pip-audit per requirements.txt, npm audit --omit=dev with annotated findings, gitleaks secret scan; PR-triggered plus weekly cron |

### Visual baseline policy

Visual baselines live in
`frameworks/playwright-ts/tests/visual.spec.ts-snapshots/` and are committed.
Regenerate them only when the intended UI has changed: run `make
visual-update` against the live target, review the diff of the PNGs, and
commit them together with the UI change that caused the diff. Never update
baselines to make a failing suite pass without inspecting the actual/expected
diffs. Baselines are maintained for chromium only; the @visual specs skip on
other browsers.

See [docs/COMPARISON.md](docs/COMPARISON.md) for an honest capability gap
analysis against reference QA portfolios.

## Demo credentials

| User | Password | Role |
|------|----------|------|
| demo | demo1234 | user |
| admin | admin1234 | admin |

## Roadmap

Phase 2 delivered: selenium-py, appium-mobile, ai-selfhealing, perf (k6 +
Locust), db-validation, and docs/COMPARISON.md.

Phase 2.5 delivered: axe-core accessibility testing and visual regression in
playwright-ts, tools/flakiness-detector, and security.yml (CodeQL, pip/npm
audit, gitleaks).

Phase 3 delivered: Pact contract testing, Karate API layer, Playwright .NET
lintas-bahasa parity, AutomationExercise (26-case) live + parity suite,
Terraform IaC, observability (/health + /metrics + dashboards), LLM-eval
harness, coverage tracking + gate, unified Visual Report, ISO/QMS pack, and
the sub-30-minute 4-shard regression gate (`make regression-30`,
`.github/workflows/regression-30min.yml`, `.gitlab-ci.yml`).
