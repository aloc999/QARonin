"""A01 Broken Access Control: the user role must never reach admin APIs.

The admin surface is GET /api/admin/orders (there is no bare /api/admin
route); a bearer token for demo/publisher must get 403, admin gets 200,
and no token gets 401.
"""

import pytest


@pytest.mark.smoke
class TestBrokenAccessControl:
    def test_demo_token_denied_admin_orders(self, api, auth_headers):
        res = api.get("/api/admin/orders", headers=auth_headers)
        assert res.status_code == 403
        assert "Admin role required" in res.json()["detail"]

    def test_admin_token_allowed(self, api, admin_headers):
        res = api.get("/api/admin/orders", headers=admin_headers)
        assert res.status_code == 200
        body = res.json()
        assert isinstance(body["count"], int)
        assert isinstance(body["orders"], list)

    def test_anonymous_denied(self, api):
        assert api.get("/api/admin/orders").status_code == 401

    def test_demo_cannot_read_foreign_order(self, api, auth_headers, admin_headers):
        mine = api.post(
            "/api/orders", headers=admin_headers,
            json={"items": [{"product_id": 1, "quantity": 1}]},
        )
        assert mine.status_code == 201
        res = api.get(f"/api/orders/{mine.json()['id']}", headers=auth_headers)
        assert res.status_code == 403
