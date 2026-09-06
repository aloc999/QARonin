# Observability

- `GET /api/health` -> `{"status":"ok"}` (CI liveness gate, Terraform manifest `health_path`).
- `GET /metrics` -> minimal Prometheus exposition (`roninshop_up`, `roninshop_build_info`), no extra deps.
- `qaronin_obs.py` -> stdlib structured JSON logs + `span()` context manager for test-run tracing.
- `prometheus.yml`, `otel-collector-config.yaml`, `grafana-dashboard.json` -> optional sidecars.

```bash
python -m pytest observability/tests -q   # or: make obs-test
```

Tier: L0 (health gate) + report enrichment. CI job: `observability`.
