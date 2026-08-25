import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.seed import seed  # noqa: E402


@pytest.fixture(scope="session")
def client():
    seed(db_url="sqlite:///./test_roninshop.db")
    with TestClient(app) as c:
        yield c
    if os.path.exists("test_roninshop.db"):
        os.remove("test_roninshop.db")


@pytest.fixture()
def user_token(client):
    res = client.post("/api/auth/login", json={"username": "demo", "password": "demo1234"})
    assert res.status_code == 200
    return res.json()["access_token"]


@pytest.fixture()
def admin_token(client):
    res = client.post("/api/auth/login", json={"username": "admin", "password": "admin1234"})
    assert res.status_code == 200
    return res.json()["access_token"]


@pytest.fixture()
def user_headers(user_token):
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture()
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}
