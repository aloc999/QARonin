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

.PHONY: help install target-up target-down test-tier-smoke test-tier-api test-tier-ui-e2e \
        test-tier-regression tier-report selenium-test selfheal-test perf-smoke db-validate \
        appium-collect ci docker-up docker-test-ui docker-test-api \
        docker-test-api-contracts docker-down clean

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

clean:
	rm -rf $(PW_DIR)/test-results $(PW_DIR)/playwright/report $(PW_DIR)/junit.xml
	rm -rf $(API_DIR)/junit.xml $(API_DIR)/test_api_framework.db
	find . -type d \( -name __pycache__ -o -name .pytest_cache \) -exec rm -rf {} +
