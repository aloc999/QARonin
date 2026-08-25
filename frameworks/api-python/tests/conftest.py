import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "apps", "demo-target")))

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.seed import seed  # noqa: E402


@pytest.fixture(scope="session")
def api():
    """
    Uses FastAPI TestClient (in-process ASGI transport) instead of a uvicorn
    subprocess. Chosen for speed: no socket binding, no process lifecycle, and
    identical coverage of the HTTP contract for an application of this size.
    Switch to a subprocess fixture if middleware/server-level behaviour needs
    to be exercised.
    """
    seed(db_url="sqlite:///./test_api_framework.db")
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def user_token(api):
    res = api.post("/api/auth/login", json={"username": "demo", "password": "demo1234"})
    assert res.status_code == 200
    return res.json()["access_token"]


@pytest.fixture(scope="session")
def admin_token(api):
    res = api.post("/api/auth/login", json={"username": "admin", "password": "admin1234"})
    assert res.status_code == 200
    return res.json()["access_token"]


@pytest.fixture()
def auth_headers(user_token):
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture()
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture()
def clean_order_state(api, admin_headers):
    """Snapshot order count before a test; tests can assert deltas cleanly."""
    before = api.get("/api/admin/orders", headers=admin_headers).json()["count"]
    yield
    after = api.get("/api/admin/orders", headers=admin_headers).json()["count"]
