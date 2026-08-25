class TestRbac:
    def test_user_cannot_access_admin_orders(self, client, user_headers):
        res = client.get("/api/admin/orders", headers=user_headers)
        assert res.status_code == 403
        assert res.json()["detail"] == "Admin role required"

    def test_admin_can_access_admin_orders(self, client, admin_headers):
        res = client.get("/api/admin/orders", headers=admin_headers)
        assert res.status_code == 200
        body = res.json()
        assert "count" in body and isinstance(body["count"], int)
        assert isinstance(body["orders"], list)

    def test_anonymous_cannot_access_admin(self, client):
        res = client.get("/api/admin/orders")
        assert res.status_code == 401

    def test_admin_can_read_any_order(self, client, admin_headers):
        orders = client.get("/api/admin/orders", headers=admin_headers).json()["orders"]
        if orders:
            res = client.get(f"/api/orders/{orders[0]['id']}", headers=admin_headers)
            assert res.status_code == 200
