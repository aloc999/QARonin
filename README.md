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
│   │                         incl. ae-parity.spec.ts vs AutomationExercise cases,
│   │                         graphql.spec.ts patterns, ALLURE/WEBKIT-gated projects)
│   ├── playwright-dotnet/    C# Playwright lintas-bahasa parity (same smoke/regression tags)
│   ├── cypress/              Cypress 15 E2E (parity) + component specs, custom commands,
│   │                         network interception, JSON fixtures
│   ├── bdd-python/           Behave Gherkin suites (auth/catalog/orders, offline)
│   ├── api-python/           pytest + requests API suite with JSON-schema contracts
│   ├── selenium-py/          Selenium 4 + pytest suite (chrome/firefox/grid, same POM)
│   ├── appium-mobile/        Appium 2 + UiAutomator2 skeleton (emulator-gated)
│   ├── karate/               Karate DSL API layer (auth/products/orders, mock-payment
│   │                         mock server, Gatling perf profile, JUnit via Maven)
│   └── automationexercise/   Live + parity suite vs automationexercise.com/test_cases (26 cases)
├── contracts/pact/           Pact consumer-driven contracts + provider verification
├── ai-selfhealing/           Agentic self-healing locator engine (offline heuristics
│                             + optional LLM agent, CLI, JSONL audit trail)
├── ai-agents/tool-loop/     Deterministic ReAct tool-use demo (offline, JSONL traces)
├── mcp-server/              QA MCP server (tier_report, coverage_gate, list_suites, pact_status)
├── evals/
│   ├── llm/                 LLM-eval harness scoring the healer (accuracy/latency JSON)
│   └── deepeval/            DeepEval RAG/conv/agent harness (judged needs OPENAI_API_KEY)
├── perf/
│   ├── k6/                   SLO-as-code load scripts (checkout, API, smoke)
│   ├── locust/               Weighted-task Locust profile with custom CSV stats
│   ├── jmeter/               JMeter smoke plan (threads, duration assertion)
│   └── README.md             tool matrix (k6/Locust/JMeter/Gatling) + gates
├── db-validation/            SQL data-validation framework (order integrity,
│                             referential checks, RBAC-vs-DB, snapshots/diffs)
├── api/
│   └── postman-newman/       Postman v2.1 collection with chained auth + Newman runner
├── infra/terraform/          Terraform IaC for ephemeral QA envs (validate/plan in CI)
├── observability/            /metrics + structured logs + Prometheus/OTel configs + dashboard
├── tools/
│   ├── flakiness-detector/   Stdlib-only Python CLI: classifies tests
│   │                         stable/flaky/broken across repeated junit runs
│   ├── visual-report/        Stdlib HTML dashboard: junit + coverage + LLM-eval
│   ├── vuln-aggregator/      Merge pip-audit/npm/gitleaks JSON into one summary
│   ├── dependency-audit/     Pin hygiene + OSV.dev check over requirements.txt
│   ├── qms-evidence/         Bundle release records with ISO/SOC2 control map
│   ├── site-monitor/         Liveness + content-drift checks with baseline
│   ├── failure-triage/       Classify JUnit failures into buckets + owners
│   ├── quality-dashboard/    Trend view across historic JUnit runs
│   ├── branch-collision/     Fail on new same-basename test collisions
│   └── claims-diff/          CSV/JSON snapshot diff for reconciliation
├── k8s/                      Target Deployment/Service + smoke Job; grid compose in docker/
├── observability/            /metrics + structured logs + Prometheus/OTel configs + dashboard,
│                             DataDog reporter (dry-run without DD_API_KEY)
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

## Prerequisites

| Tool | Minimum version | Needed for | Install |
|------|----------------|------------|---------|
| Python | 3.11+ | demo-target, api/db/contract suites, all `tools/*`, evals | `python3 --version` |
| Node.js | 22 LTS | Playwright-TS, Cypress, Newman | `node --version` |
| Java | 17 | Karate, Gatling | `java -version` |
| Maven | 3.9+ | Karate, Gatling (runners ship it; local: `mvn -version`) | — |
| .NET | 6 SDK (build) / 8+ runtime OK via `DOTNET_ROLL_FORWARD=Major` | Playwright-C# | `dotnet --list-sdks` |
| Terraform | >= 1.6 | `infra/terraform` validate/plan | `terraform version` |
| Docker | any recent | Grid compose, ZAP/JMeter images, `docker compose config` lint | `docker --version` |
| PowerShell | 7+ | Playwright browser install for .NET (`playwright.ps1`) | `pwsh --version` |
| Optional | — | DeepEval judged metrics: `OPENAI_API_KEY`; DataDog ship: `DD_API_KEY`; Slack notify: `SLACK_WEBHOOK_URL`; live reference: `AE_LIVE=1`, `GQL_LIVE=1` | env vars |

Python packages are pinned per suite (`requirements.txt` next to each suite);
Node packages per `package.json` + committed lockfiles. No root venv needed.

## Setup

```bash
git clone https://github.com/aloc999/QARonin.git && cd QARonin

# Shortcut for the basics (Python API deps + Playwright browsers + Newman):
make install
# Cypress / .NET / BDD / Java need their own steps below.

# 1. Python suites (demo-target + api-python; repeat pattern per suite)
pip install -r apps/demo-target/requirements.txt -r frameworks/api-python/requirements.txt

# 2. Playwright-TS browsers (chromium + firefox)
cd frameworks/playwright-ts && npm ci && npx playwright install chromium firefox && cd ../..

# 3. Newman
cd api/postman-newman && npm install && cd ../..

# 4. Cypress (E2E + component)
cd frameworks/cypress && npm install && cd ../..

# 5. .NET parity suite + its browsers
dotnet build frameworks/playwright-dotnet
pwsh frameworks/playwright-dotnet/bin/Debug/net6.0/playwright.ps1 install chromium

# 6. BDD + misc Python (behave, mcp, deepeval as needed)
pip install -r frameworks/bdd-python/requirements.txt
pip install mcp   # only for mcp-server / mcp-test

# 7. Start the system under test
make target-up                 # RoninShop on http://127.0.0.1:8199
curl -sf http://127.0.0.1:8199/api/health   # readiness probe (also used by CI/k8s)
```

Demo credentials: `demo/demo1234` (user), `admin/admin1234` (admin).

## Running suites

Every suite runs headless by default (CI mode). Headed runs open a visible
browser for debugging.

```bash
make ci              # L0+L1 gate: target pytest -> api suite -> smoke -> budget report
make regression-30   # full gate: 4 parallel shards, hard 30-min budget (needs target-up)
```

| Suite | Headless (default) | Headed (debug) |
|-------|-------------------|----------------|
| Playwright-TS | `cd frameworks/playwright-ts && npx playwright test` | `npx playwright test --headed` (add `--project=chromium --grep @smoke` to focus) |
| Playwright-C# | `make csharp-test` | `cd frameworks/playwright-dotnet && dotnet test --no-build --filter Category=smoke` with headed config: set `Headless=false` via `HEADED=1`? Not wired — run with `PWDEBUG=1 dotnet test ...` for inspector |
| Cypress E2E | `make cypress-test` (`cypress run --e2e`) | `cd frameworks/cypress && npx cypress open` (interactive runner) |
| Cypress component | `make cypress-component` | `npx cypress open --component` |
| Selenium | `make selenium-test` (headless by default) | `HEADLESS=0 BROWSER=chrome python -m pytest frameworks/selenium-py -m smoke` |
| Appium | `make appium-collect` (skips without `RUN_APPIUM=1` + emulator) | start emulator, `RUN_APPIUM=1 python -m pytest frameworks/appium-mobile` |
| API Python | `cd frameworks/api-python && pytest` | n/a (no browser) — add `-v` / `-x` / `-k name` to focus |
| Behave BDD | `make bdd-test` | n/a — `behave --tags=@smoke` when tags exist |
| Karate | `make karate-test` (needs `mvn`) | n/a — `-Dkarate.options="--tags @smoke"` to focus |
| Newman | `cd api/postman-newman && npm test` | `npm run test:verbose` |
| JMeter | `make perf-jmeter` (needs `jmeter`) | open `perf/jmeter/smoke.jmx` in the JMeter GUI |
| Gatling | `mvn -f frameworks/karate/pom.xml test-compile gatling:test -Pperf` (needs target) | reports open from `target/gatling/<run>/index.html` |

Focusing tips: `pytest -k`, `behave -n`, `--grep @smoke`, `--filter Category=smoke`,
`-Dkarate.options="--tags @smoke"`, `cypress run --spec`.

## Test reports

| Report | How to generate | Output |
|--------|----------------|--------|
| JUnit XML (per suite) | produced by every run (`pytest --junitxml`, Playwright `junit`, Newman junit, surefire) | `**/junit.xml`, `newman-report.xml` |
| Unified visual report | `make visual-report` | `reports/visual-report.html` |
| Trend dashboard | `make dashboard` (reads `reports/history/junit-*.xml`) | `reports/quality-dashboard.html` |
| Coverage + gate | `make coverage` (86%+ typical; gate `--min 0.5`) | `coverage.xml`, terminal summary |
| Tier budgets | `make tier-report` | pass/fail per suite vs budget |
| Allure (Playwright-TS) | `ALLURE=1 npx playwright test` then `npx allure generate allure-results` (needs the `allure` CLI: `npm i -D allure-commandline` or system package) | `allure-report/` |
| Cypress videos/screenshots | automatic on failure | `frameworks/cypress/cypress/{videos,screenshots}/` |
| Newman HTML | `cd api/postman-newman && npm run test:html` | `newman-report.html` |
| Gatling | after a `-Pperf` run | `frameworks/karate/target/gatling/*/index.html` |
| Vuln summary | `make vuln-report` (after producing audit JSONs) | `reports/vuln-summary.md` |
| Failure triage | `make triage` | `reports/failure-triage.json` |
| QMS evidence pack | `make qms-evidence` | `reports/qms-evidence/<stamp>/` + `manifest.json` |
| LLM evals | `python evals/llm/eval.py` | `evals/llm/eval-report.json` |

## Code quality policy (enforced)

- **No hard-coded waits.** Fixed sleeps (`waitForTimeout`, `time.sleep`,
  `Thread.sleep`, `Task.Delay`, `cy.wait(ms)`, implicit waits) are banned in
  test code and rejected by `make lint-tests` (runs in CI `lint`). Use:
  Playwright auto-retry assertions, Selenium `WebDriverWait` (`utils/waits.py`,
  `utils/mobile_wait.py`), `cy.wait(@alias)`, conditional readiness probes.
  Legitimate exceptions (retry-backoff under test, k6 think time, CI service
  probes) are documented in code or `strategy/scripts/no_hard_waits.allowlist`.
- **Meaningful assertions.** Assert behavior, not existence: exact texts,
  counts, shapes (`order_id` starts with `#` + digits), status codes *plus*
  bodies, totals recomputed from inputs. No `assert True` placeholders
  (grep-verified).
- **No new test-module collisions.** Same-basename `test_*.py` across suites
  breaks combined collection; `tools/branch-collision/monitor.py` fails the
  build on anything outside `allowlist.txt`.
- **Coverage must not decline**: `strategy/scripts/coverage_gate.py --min 0.5`.

Individual pieces (everything behind `make help`):

```bash
make target-up                 # start RoninShop on http://127.0.0.1:8199
cd frameworks/playwright-ts && npx playwright test    # UI suites (all browsers)
cd frameworks/api-python && pytest                    # API suite incl. contracts
cd api/postman-newman && npm test                     # Newman collection run

make selenium-test             # Selenium 4 suite (smoke + regression markers)
make pact-test                 # Pact consumer + provider contracts (L1)
make bdd-test                  # Behave Gherkin suites (offline)
make cypress-test              # Cypress E2E vs live target (needs npm install)
make deepeval                  # DeepEval harness (offline guards; judged need key)
make agent-test                # tool-loop agent tests (needs live target)
make mcp-test                  # MCP protocol tests
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
| [frameworks/karate](frameworks/karate) | Java 17, Karate 1.4 + JUnit5 (+ Gatling 3.12 perf profile) | auth/products/orders DSL, mock-payment mock server, Gatling sim |
| [frameworks/cypress](frameworks/cypress) | TypeScript/JS, Cypress 15 | E2E parity, component spec, custom commands, cy.intercept patterns |
| [frameworks/bdd-python](frameworks/bdd-python) | Python, Behave | Gherkin auth/catalog/orders, offline TestClient |
| [frameworks/playwright-dotnet](frameworks/playwright-dotnet) | C#, Playwright 1.40 + NUnit (.NET 6) | lintas-bahasa parity: same @smoke/@regression tags as TS |
| [frameworks/automationexercise](frameworks/automationexercise) | Python, pytest + requests | live reference checks (cases 1-26) + offline RoninShop parity |
| [evals/llm](evals/llm) | Python | fixed JSONL healer dataset, accuracy/latency gate, eval-report.json |
| [evals/deepeval](evals/deepeval) | Python, DeepEval | RAG/conv/agent judged metrics (key-gated) + offline guards |
| [ai-agents/tool-loop](ai-agents/tool-loop) | Python | deterministic ReAct demo over local tools, JSONL traces |
| [mcp-server](mcp-server) | Python, MCP SDK | tier_report/coverage_gate/list_suites/pact_status over stdio |
| [infra/terraform](infra/terraform) | Terraform >= 1.6 | ephemeral QA env manifest, credential-free validate/plan in CI |
| [observability](observability) | Python stdlib + FastAPI | /api/health, /metrics (Prometheus), JSONL spans, OTel/Prom configs, Grafana dashboard |
| [tools/visual-report](tools/visual-report) | Python stdlib | one HTML dashboard from junit + coverage + LLM-eval |
| [tools/qms-evidence](tools/qms-evidence) | Python stdlib | evidence pack with ISO/SOC2 control mapping |
| [k8s](k8s) | YAML | target Deployment/Service/smoke Job; Selenium Grid compose profile |
| [security](.github/workflows/regression-30min.yml) | ZAP baseline (informational) + CodeQL/audits/gitleaks | zap-baseline job, vuln-aggregator summary |
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
