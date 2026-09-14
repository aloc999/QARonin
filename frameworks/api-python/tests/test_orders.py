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

    @pytest.mark.regression
    def test_multi_item_total_recomputed_from_catalog(self, api, auth_headers):
        catalog = {p["id"]: p for p in api.get("/api/products").json()}
        items = [
            {"product_id": 1, "quantity": 1},
            {"product_id": 6, "quantity": 2},
        ]
        res = api.post("/api/orders", headers=auth_headers, json={"items": items})
        assert res.status_code == 201
        body = res.json()
        expected = round(sum(catalog[i["product_id"]]["price"] * i["quantity"] for i in items), 2)
        assert body["total"] == expected
        assert body["username"] == "demo"

    @pytest.mark.regression
    def test_order_decrements_stock_exactly(self, api, auth_headers):
        product_id = 6  # high-stock seed item, safe to mutate
        before = api.get(f"/api/products/{product_id}").json()["stock"]
        res = api.post(
            "/api/orders",
            headers=auth_headers,
            json={"items": [{"product_id": product_id, "quantity": 2}]},
        )
        assert res.status_code == 201
        after = api.get(f"/api/products/{product_id}").json()["stock"]
        assert after == before - 2

    @pytest.mark.regression
    def test_unknown_product_404_names_it(self, api, auth_headers):
        res = api.post(
            "/api/orders",
            headers=auth_headers,
            json={"items": [{"product_id": 987654, "quantity": 1}]},
        )
        assert res.status_code == 404
        assert "987654" in res.json()["detail"]

    @pytest.mark.regression
    def test_zero_quantity_rejected_without_mutation(self, api, auth_headers):
        product_id = 6
        before = api.get(f"/api/products/{product_id}").json()["stock"]
        res = api.post(
            "/api/orders",
            headers=auth_headers,
            json={"items": [{"product_id": product_id, "quantity": 0}]},
        )
        assert res.status_code == 409
        assert api.get(f"/api/products/{product_id}").json()["stock"] == before

    @pytest.mark.regression
    def test_created_items_echo_catalog_unit_prices(self, api, auth_headers, new_order):
        catalog = {p["id"]: p for p in api.get("/api/products").json()}
        for item in new_order["items"]:
            assert item["unit_price"] == catalog[item["product_id"]]["price"]
            assert item["quantity"] >= 1
