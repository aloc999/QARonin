# Kubernetes + Selenium Grid

- `k8s/target-deployment.yaml` — RoninShop target (probes hit `/api/health`).
- `k8s/target-service.yaml` — ClusterIP service + `qaronin-smoke` Job running
  the API suite inside the cluster (`BASE_URL=http://roninshop-target:8199`).
- `docker/docker-compose.grid.yml` — Selenium Grid hub + chrome/firefox/edge
  nodes for `selenium-py` (`SELENIUM_REMOTE_URL`) and Cypress.

```bash
kubectl apply -f k8s/ --dry-run=client    # or: make k8s-lint
docker compose -f docker/docker-compose.grid.yml config  # grid file check
SELENIUM_REMOTE_URL=http://127.0.0.1:4444/wd/hub python -m pytest frameworks/selenium-py
```

CI job: `k8s` (dry-run + kubeconform-style schema check via python).
Images `qaronin/target:latest` / `qaronin/api-tests:latest` come from
`docker/` Dockerfiles; build+push is a release step, not a merge gate.
