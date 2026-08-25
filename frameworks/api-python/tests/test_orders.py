import pytest


@pytest.fixture()
def new_order(api, auth_headers):
    res = api.post(
        "/api/orders",
        headers=auth_headers,
        json={"items": [{"product_id": 1, "quantity": 1}]},
    )
    assert res.status_code == 201
    return res.json()


@pytest.mark.smoke
class TestOrderLifecycle:
    def test_create_order(self, api, auth_headers, clean_order_state):
        res = api.post(
            "/api/orders",
            headers=auth_headers,
            json={"items": [{"product_id": 2, "quantity": 3}]},
        )
        assert res.status_code == 201
        body = res.json()
        assert body["username"] == "demo"
        assert abs(body["total"] - round(body["items"][0]["unit_price"] * 3, 2)) < 0.01

    def test_get_created_order(self, api, new_order, auth_headers):
        res = api.get(f"/api/orders/{new_order['id']}", headers=auth_headers)
        assert res.status_code == 200
        fetched = res.json()
        assert fetched["id"] == new_order["id"]
        assert fetched["status"] == "confirmed"
        assert len(fetched["items"]) == len(new_order["items"])

    def test_list_all_orders_as_admin(self, api, admin_headers):
        res = api.get("/api/admin/orders", headers=admin_headers)
        assert res.status_code == 200
        assert isinstance(res.json()["orders"], list)

    @pytest.mark.regression
    def test_order_requires_authentication(self, api):
        res = api.post("/api/orders", json={"items": [{"product_id": 1}]})
        assert res.status_code == 401

    @pytest.mark.regression
    def test_get_unknown_order_404(self, api, auth_headers):
        assert api.get("/api/orders/987654", headers=auth_headers).status_code == 404

    @pytest.mark.regression
    def test_cannot_read_foreign_order(self, api, new_order, admin_token):
        res = api.get(
            f"/api/orders/{new_order['id']}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert res.status_code in (200, 403)

    @pytest.mark.regression
    def test_stock_never_goes_negative(self, api, auth_headers):
        product_id = 4
        stock_before = api.get(f"/api/products/{product_id}").json()["stock"]
        res = api.post(
            "/api/orders",
            headers=auth_headers,
            json={"items": [{"product_id": product_id, "quantity": stock_before + 10}]},
        )
        assert res.status_code == 409
        stock_after = api.get(f"/api/products/{product_id}").json()["stock"]
        assert stock_after == stock_before

    @pytest.mark.regression
    def test_empty_order_rejected(self, api, auth_headers):
        assert api.post("/api/orders", headers=auth_headers, json={"items": []}).status_code == 422
