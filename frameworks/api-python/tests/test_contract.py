import json
import os

import jsonschema
import pytest

SCHEMAS_DIR = os.path.join(os.path.dirname(__file__), "..", "schemas")


def load_schema(name):
    with open(os.path.join(SCHEMAS_DIR, name)) as f:
        return json.load(f)


@pytest.mark.contract
class TestContracts:
    def test_login_response_contract(self, api):
        res = api.post("/api/auth/login", json={"username": "demo", "password": "demo1234"})
        assert res.status_code == 200
        jsonschema.validate(res.json(), load_schema("login_response.schema.json"))

    def test_admin_login_response_contract(self, api):
        res = api.post("/api/auth/login", json={"username": "admin", "password": "admin1234"})
        assert res.status_code == 200
        jsonschema.validate(res.json(), load_schema("login_response.schema.json"))

    def test_products_list_contract(self, api):
        res = api.get("/api/products")
        assert res.status_code == 200
        jsonschema.validate(res.json(), load_schema("products_list.schema.json"))

    def test_product_detail_contract(self, api):
        res = api.get("/api/products/1")
        assert res.status_code == 200
        jsonschema.validate(res.json(), load_schema("product_detail.schema.json"))

    def test_order_contract(self, api, auth_headers):
        created = api.post(
            "/api/orders",
            headers=auth_headers,
            json={"items": [{"product_id": 6, "quantity": 2}]},
        )
        assert created.status_code == 201
        jsonschema.validate(created.json(), load_schema("order.schema.json"))

    def test_admin_orders_contract(self, api, admin_headers):
        res = api.get("/api/admin/orders", headers=admin_headers)
        assert res.status_code == 200
        jsonschema.validate(res.json(), load_schema("admin_orders.schema.json"))

    def test_flaky_success_contract(self, api):
        for _ in range(15):
            res = api.get("/api/flaky")
            if res.status_code == 200:
                body = res.json()
                assert body["status"] == "ok"
                return
        pytest.fail("flaky endpoint never succeeded in 15 attempts")
