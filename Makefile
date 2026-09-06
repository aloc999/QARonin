ROOT := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
PY := python3
TARGET_DIR := apps/demo-target
PW_DIR := frameworks/playwright-ts
API_DIR := frameworks/api-python
SELENIUM_DIR := frameworks/selenium-py
SELFHEAL_DIR := ai-selfhealing
PERF_K6_DIR := perf/k6
PERF_LOCUST_DIR := perf/locust
DBVAL_DIR := db-validation
APPIUM_DIR := frameworks/appium-mobile
FLAKE_DIR := tools/flakiness-detector

.PHONY: help install target-up target-down test-tier-smoke test-tier-api test-tier-ui-e2e \
        test-tier-regression tier-report selenium-test selfheal-test perf-smoke db-validate \
        appium-collect visual-update flake-check ci docker-up docker-test-ui docker-test-api \
        docker-test-api-contracts docker-down clean pact-test karate-test csharp-build \
        csharp-install csharp-test tf-validate tf-plan obs-test llm-eval ae-test coverage visual-report \
        regression-30

help:
	@echo "QARonin - make targets"
	@echo ""
	@echo "  install              Install dependencies for all frameworks"
	@echo "  target-up            Start the demo target on 127.0.0.1:8199"
	@echo "  target-down          Stop the demo target"
	@echo "  test-tier-smoke      L0 smoke (playwright @smoke)"
	@echo "  test-tier-api        L1 API regression (api-python + newman + target pytest)"
	@echo "  test-tier-ui-e2e     L2 UI e2e + regression (playwright chromium)"
	@echo "  test-tier-regression L3 full cross-browser playwright suite"
	@echo "  tier-report          Parse junit.xml reports and check budgets"
	@echo "  ci                   Run the PR gate (L0 + L1)"
	@echo "  docker-up            Start compose stack (target + postgres)"
	@echo "  docker-test-ui       Run playwright suite against compose target"
	@echo "  docker-test-api      Run api-python suite against compose target"
	@echo "  docker-test-api-contracts  Run api-python contract tests in container"
	@echo "  docker-down          Tear down compose stack"
	@echo "  selenium-test        Selenium suite (smoke+regression) vs live target"
	@echo "  selfheal-test        Self-healing engine pytest suite (offline)"
	@echo "  perf-smoke           k6 + locust quick load runs vs live target"
	@echo "  db-validate          DB validation suite against the demo target DB"
	@echo "  appium-collect       Collect mobile tests (skips unless RUN_APPIUM=1)"
	@echo "  visual-update        Regenerate Playwright visual baselines (chromium)"
	@echo "  flake-check          Flakiness detector report over its fixtures"
	@echo "  pact-test            Pact consumer + provider contract tests"
	@echo "  karate-test          Karate API suite vs live target (needs mvn)"
	@echo "  csharp-build         Build Playwright .NET parity suite (needs dotnet)"
	@echo "  csharp-install       Download Playwright browsers for .NET driver (needs pwsh)"
	@echo "  csharp-test          Run C# smoke tests vs live target"
	@echo "  tf-validate          Terraform init + validate (skips if missing)"
	@echo "  tf-plan              Terraform validate + plan"
	@echo "  obs-test             Observability contract tests"
	@echo "  llm-eval             LLM self-heal eval harness"
	@echo "  ae-test              AutomationExercise parity (AE_LIVE=0 offline)"
	@echo "  coverage             Pytest-cov across python suites + gate"
	@echo "  visual-report        Unified HTML dashboard from junit/coverage/eval"
	@echo "  regression-30        Full regression, 4 parallel shards, 30-min gate"

install:
	cd $(API_DIR) && pip install -r requirements.txt -r ../../apps/demo-target/requirements.txt
	cd $(PW_DIR) && npm install && npx playwright install chromium firefox
	cd api/postman-newman && npm install

target-up:
	cd $(TARGET_DIR) && nohup $(PY) -m uvicorn app.main:app --host 127.0.0.1 --port 8199 > /tmp/qaronin-target.log 2>&1 & \
	for i in $$(seq 1 30); do curl -sf http://127.0.0.1:8199/api/products > /dev/null && exit 0 || sleep 1; done; \
	echo "target failed to start; see /tmp/qaronin-target.log" && exit 1

target-down:
	-pkill -f "uvicorn app.main:app"

wait-target:
	for i in $$(seq 1 30); do curl -sf http://127.0.0.1:8199/api/products > /dev/null && exit 0 || sleep 1; done; \
	echo "target not reachable on 8199" && exit 1

test-tier-smoke: target-up
	cd $(PW_DIR) && npx playwright test --grep @smoke

test-tier-api: target-up
	cd $(API_DIR) && $(PY) -m pytest --junitxml=junit.xml
	cd api/postman-newman && npm test
	cd $(TARGET_DIR) && $(PY) -m pytest tests

test-tier-ui-e2e: target-up
	cd $(PW_DIR) && npx playwright test --project=chromium --grep "@e2e|@regression"

test-tier-regression: target-up
	cd $(PW_DIR) && npx playwright test

visual-update: target-up
	cd $(PW_DIR) && npx playwright test tests/visual.spec.ts \
		--project=chromium --update-snapshots

flake-check:
	$(PY) $(FLAKE_DIR)/flakiness_detector.py "$(FLAKE_DIR)/fixtures/run-*.xml"

tier-report:
	$(PY) strategy/scripts/tier_report.py \
		strategy/fixtures/ui.xml strategy/fixtures/api.xml strategy/fixtures/newman.xml \
		--budget ui=600 --budget api=300 --budget newman=120

selenium-test: target-up
	cd $(SELENIUM_DIR) && $(PY) -m pytest

selfheal-test:
	cd $(SELFHEAL_DIR) && PYTHONPATH=. $(PY) -m pytest

perf-smoke: target-up
	k6 run $(PERF_K6_DIR)/smoke.js || echo "k6 not installed; see $(PERF_K6_DIR)/README.md"
	cd $(PERF_LOCUST_DIR) && locust -f locustfile.py --headless -u 5 -r 1 -t 20s \
		--host http://127.0.0.1:8199

db-validate: target-up
	cd $(DBVAL_DIR) && $(PY) -m pytest

appium-collect:
	cd $(APPIUM_DIR) && $(PY) -m pytest --collect-only -q

ci: target-up
	cd $(TARGET_DIR) && $(PY) -m pytest tests
	cd $(API_DIR) && $(PY) -m pytest --junitxml=junit.xml
	cd $(PW_DIR) && npx playwright test --grep @smoke
	make tier-report

docker-up:
	cd docker && docker compose up -d --build target postgres

docker-test-ui: docker-up
	cd docker && docker compose run --rm ui-tests

docker-test-api: docker-up
	cd docker && docker compose run --rm api-tests

docker-test-api-contracts: docker-up
	cd docker && docker compose run --rm api-tests python -m pytest tests/test_contract.py

docker-down:
	cd docker && docker compose down -v

pact-test:
	cd contracts/pact && $(PY) -m pytest tests -q

karate-test: target-up
	command -v mvn >/dev/null || (echo "mvn not installed; skipping karate" && exit 0)
	cd frameworks/karate && mvn test

csharp-build:
	command -v dotnet >/dev/null || (echo "dotnet not installed; skipping" && exit 0)
	dotnet build frameworks/playwright-dotnet

csharp-install: csharp-build
	command -v pwsh >/dev/null || (echo "pwsh not installed; install browsers manually, see frameworks/playwright-dotnet/README.md" && exit 0)
	pwsh frameworks/playwright-dotnet/bin/Debug/net6.0/playwright.ps1 install chromium

csharp-test: target-up csharp-build
	cd frameworks/playwright-dotnet && BASE_URL=http://127.0.0.1:8199 dotnet test --no-build --filter "Category=smoke"

tf-validate:
	command -v terraform >/dev/null || (echo "terraform not installed; skipping" && exit 0)
	cd infra/terraform && terraform init -backend=false && terraform validate

tf-plan: tf-validate
	cd infra/terraform && terraform plan -no-color

obs-test:
	$(PY) -m pytest observability/tests -q

llm-eval:
	$(PY) evals/llm/eval.py
	cd evals/llm && $(PY) -m pytest tests -q

ae-test:
	cd frameworks/automationexercise && AE_LIVE=0 $(PY) -m pytest tests -q

# Per-suite runs in their own dirs (same-basename modules collide in one pytest
# invocation; some suites also rely on CWD for imports). COVERAGE_FILE keeps
# one shared data file; --cov-append merges; the last run writes the XML.
export COVERAGE_FILE := $(CURDIR)/.coverage
export COVERAGE_RCFILE := $(CURDIR)/.coveragerc
coverage: target-up
	$(PY) -c "import pytest_cov" 2>/dev/null || pip install pytest-cov
	rm -f coverage.xml .coverage .coverage.*
	cd apps/demo-target && $(PY) -m pytest tests -q --cov=app --cov-append --cov-report=
	cd frameworks/api-python && $(PY) -m pytest -q --cov=. --cov-append --cov-report=
	cd contracts/pact && $(PY) -m pytest tests -q --cov=. --cov-append --cov-report=
	cd observability && $(PY) -m pytest tests -q --cov=. --cov-append --cov-report=
	cd db-validation && $(PY) -m pytest -q --cov=dbval --cov-append --cov-report=
	cd ai-selfhealing && PYTHONPATH=. $(PY) -m pytest -q --cov=selfheal --cov-append --cov-report=
	cd evals/llm && $(PY) -m pytest tests -q --cov=. --cov-append --cov-report=
	cd frameworks/automationexercise && AE_LIVE=0 $(PY) -m pytest tests -q --cov=. --cov-append --cov-report=
	$(PY) -m pytest tools/visual-report/tests tools/flakiness-detector/tests strategy/tests -q --cov=tools --cov=strategy --cov-append --cov-report=xml:coverage.xml --cov-report=term
	$(PY) strategy/scripts/coverage_gate.py coverage.xml --min 0.5

visual-report:
	$(PY) tools/visual-report/generate.py --junit "frameworks/playwright-ts/junit.xml" --junit "frameworks/api-python/junit.xml" --junit "api/postman-newman/newman-report.xml" --coverage coverage.xml --llm-eval evals/llm/eval-report.json -o reports/visual-report.html || $(PY) tools/visual-report/generate.py -o reports/visual-report.html

regression-30:
	$(PY) strategy/scripts/regression_30.py

clean:
	rm -rf $(PW_DIR)/test-results $(PW_DIR)/playwright/report $(PW_DIR)/junit.xml
	rm -rf $(API_DIR)/junit.xml $(API_DIR)/test_api_framework.db
	find . -type d \( -name __pycache__ -o -name .pytest_cache \) -exec rm -rf {} +
