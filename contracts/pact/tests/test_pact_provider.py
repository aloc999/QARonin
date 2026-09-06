"""Pact provider verification (roninshop-provider).

Replays every interaction from the checked-in pact file against the real
demo-target FastAPI app (in-process TestClient, same pattern as
frameworks/api-python). Type-flexible matchers (MATCH_STRING / min-length)
mirror Pact v2 matching rules without requiring a broker.
"""

import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "apps", "demo-target")
    ),
)

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.seed import seed  # noqa: E402

PACT_FILE = Path(__file__).resolve().parent.parent / "pacts" / "roninshop-consumer-roninshop-provider.json"


@pytest.fixture(scope="module")
def provider():
    seed(db_url="sqlite:///./test_pact_provider.db")
    with TestClient(app) as c:
        yield c


def _load_pact():
    with open(PACT_FILE) as f:
        return json.load(f)


def _resolve_auth(headers, provider):
    """Replace the MATCH_STRING bearer placeholder with a real token."""
    headers = dict(headers or {})
    auth = headers.get("Authorization", "")
    if "MATCH_STRING" in auth:
        res = provider.post("/api/auth/login", json={"username": "demo", "password": "demo1234"})
        assert res.status_code == 200
        headers["Authorization"] = f"Bearer {res.json()['access_token']}"
    return headers


def test_provider_verifies_all_pact_interactions(provider):
    pact = _load_pact()
    failures = []
    for ix in pact["interactions"]:
        req = ix["request"]
        method = req["method"]
        path = req["path"]
        headers = _resolve_auth(req.get("headers"), provider)
        body = req.get("body")
        kwargs = {"headers": headers}
        if body is not None and method in ("POST", "PUT", "PATCH"):
            kwargs["json"] = body
        res = provider.request(method, path, **kwargs)
        expected = ix["response"]["status"]
        if res.status_code != expected:
            failures.append(f"{ix['description']}: expected {expected}, got {res.status_code} ({res.text[:200]})")
            continue
        # Spot-check response body keys where the pact pins them.
        for key, val in (ix["response"].get("body") or {}).items() if isinstance(ix["response"].get("body"), dict) else []:
            if val in ("MATCH_STRING", 1.0, 1) or key in ("status", "token_type", "username"):
                payload = res.json()
                assert key in payload, f"{ix['description']}: missing key {key}"
    assert not failures, "pact provider verification failed:\n" + "\n".join(failures)


def test_provider_login_contract_shape(provider):
    res = provider.post("/api/auth/login", json={"username": "demo", "password": "demo1234"})
    assert res.status_code == 200
    body = res.json()
    for key in ("access_token", "token_type", "username", "role"):
        assert key in body
    assert body["token_type"] == "bearer"


def test_provider_products_contract_shape(provider):
    res = provider.get("/api/products")
    assert res.status_code == 200
    items = res.json()
    assert isinstance(items, list) and len(items) >= 1
    for key in ("id", "name", "price", "stock"):
        assert key in items[0]
