"""Observability contract tests: /api/health, /metrics, structured logs."""

import json
import os
import sys

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "apps", "demo-target")),
)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")))

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.seed import seed  # noqa: E402
from observability.qaronin_obs import log_event  # noqa: E402


def _client():
    seed(db_url="sqlite:///./test_obs.db")
    return TestClient(app)


def test_health_endpoint():
    with _client() as c:
        res = c.get("/api/health")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"


def test_metrics_prometheus_exposition():
    with _client() as c:
        res = c.get("/metrics")
        assert res.status_code == 200
        assert "roninshop_up 1" in res.text
        assert res.headers["content-type"].startswith("text/plain")


def test_structured_log_is_json():
    rec = log_event("info", "unit-test", suite="observability")
    assert rec["level"] == "info"
    assert rec["suite"] == "observability"
    json.dumps(rec)  # must serialize
