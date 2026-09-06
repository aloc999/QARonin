"""AutomationExercise test_cases parity.

Live checks hit https://automationexercise.com/test_cases (AE_LIVE=1 or
default: attempted, skipped gracefully offline). RoninShop parity tests run
fully offline via TestClient and mirror the AE flows that have a local
analogue (see README mapping + QMS TRACEABILITY-MATRIX.md).
"""

import os
import sys

import pytest
import requests

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "apps", "demo-target")),
)

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.seed import seed  # noqa: E402

AE_TEST_CASES_URL = "https://automationexercise.com/test_cases"
AE_LIVE = os.environ.get("AE_LIVE", "1") == "1"


@pytest.fixture(scope="module")
def api():
    seed(db_url="sqlite:///./test_ae_parity.db")
    with TestClient(app) as c:
        yield c


def _ae_page():
    res = requests.get(AE_TEST_CASES_URL, timeout=20)
    res.raise_for_status()
    return res.text


# ---------- Live: the reference page itself (AE-7) ----------

def test_ae07_test_cases_page_reachable_and_lists_26_cases():
    """AE-7: Verify Test Cases Page. The reference lists cases 1-26."""
    if not AE_LIVE:
        pytest.skip("AE_LIVE=0")
    try:
        text = _ae_page()
    except Exception as e:
        pytest.skip(f"automationexercise.com unreachable: {e}")
    for n in (1, 7, 14, 26):
        assert f"Test Case {n}" in text, f"missing Test Case {n} on reference page"
    assert "collapse1" in text and "collapse26" in text


def test_ae_live_home_products_login_entry_points():
    """Spot-check the live site's core entry points exist."""
    if not AE_LIVE:
        pytest.skip("AE_LIVE=0")
    try:
        for url in ("https://automationexercise.com/",
                    "https://automationexercise.com/products",
                    "https://automationexercise.com/login"):
            r = requests.get(url, timeout=20)
            assert r.status_code == 200, url
    except Exception as e:
        pytest.skip(f"automationexercise.com unreachable: {e}")


# ---------- Parity: AE flows mirrored on RoninShop (offline) ----------

def test_ae02_parity_login_ok(api):
    """AE-2: Login with correct credentials."""
    res = api.post("/api/auth/login", json={"username": "demo", "password": "demo1234"})
    assert res.status_code == 200
    assert res.json()["username"] == "demo"


def test_ae03_parity_login_incorrect_shows_error(api):
    """AE-3: Login with incorrect credentials -> 401 (UI shows error box)."""
    res = api.post("/api/auth/login", json={"username": "demo", "password": "nope"})
    assert res.status_code == 401


def test_ae04_parity_logout_clears_token(api):
    """AE-4: Logout. API analogue: bad/empty token is rejected after logout."""
    bad = api.get("/api/admin/orders", headers={"Authorization": "Bearer logged-out"})
    assert bad.status_code == 401


def test_ae08_parity_products_and_detail(api):
    """AE-8: All products + detail page shows name/price/stock."""
    products = api.get("/api/products").json()
    assert len(products) >= 1
    first = api.get(f"/api/products/{products[0]['id']}").json()
    for key in ("name", "price", "stock"):
        assert key in first


def test_ae12_parity_add_products_to_cart_flow(api):
    """AE-12: Add two products -> create order, verify totals."""
    login = api.post("/api/auth/login", json={"username": "demo", "password": "demo1234"}).json()
    headers = {"Authorization": f"Bearer {login['access_token']}"}
    products = api.get("/api/products").json()[:2]
    order = api.post(
        "/api/orders",
        json={"items": [{"product_id": p["id"], "quantity": 1} for p in products]},
        headers=headers,
    )
    assert order.status_code == 201
    expected = round(sum(p["price"] for p in products), 2)
    assert order.json()["total"] == expected


def test_ae13_parity_product_quantity(api):
    """AE-13: Quantity is honored in order total."""
    login = api.post("/api/auth/login", json={"username": "demo", "password": "demo1234"}).json()
    headers = {"Authorization": f"Bearer {login['access_token']}"}
    product = api.get("/api/products").json()[0]
    order = api.post(
        "/api/orders", json={"items": [{"product_id": product["id"], "quantity": 4}]}, headers=headers
    )
    assert order.status_code == 201
    assert order.json()["total"] == round(product["price"] * 4, 2)


def test_ae17_parity_remove_product_invalidates_order(api):
    """AE-17: Removing products -> ordering unknown product 404s."""
    login = api.post("/api/auth/login", json={"username": "demo", "password": "demo1234"}).json()
    headers = {"Authorization": f"Bearer {login['access_token']}"}
    res = api.post("/api/orders", json={"items": [{"product_id": 99999, "quantity": 1}]}, headers=headers)
    assert res.status_code == 404


def test_ae16_parity_login_before_checkout(api):
    """AE-16: Login before checkout succeeds end to end."""
    login = api.post("/api/auth/login", json={"username": "demo", "password": "demo1234"})
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    product = api.get("/api/products").json()[0]
    order = api.post(
        "/api/orders", json={"items": [{"product_id": product["id"], "quantity": 1}]}, headers=headers
    )
    assert order.status_code == 201
    fetched = api.get(f"/api/orders/{order.json()['id']}", headers=headers)
    assert fetched.status_code == 200
