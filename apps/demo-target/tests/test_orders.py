class TestOrderCreation:
    def test_create_order_happy_path(self, client, user_headers):
        products = client.get("/api/products").json()
        first = products[0]
        res = client.post(
            "/api/orders",
            headers=user_headers,
            json={"items": [{"product_id": first["id"], "quantity": 2}]},
        )
        assert res.status_code == 201
        order = res.json()
        assert order["id"] > 0
        assert order["status"] == "confirmed"
        expected_total = round(first["price"] * 2, 2)
        assert abs(order["total"] - expected_total) < 0.01
        assert order["username"] == "demo"
        assert len(order["items"]) == 1
        assert order["items"][0]["quantity"] == 2

    def test_create_order_requires_auth(self, client):
        res = client.post("/api/orders", json={"items": [{"product_id": 1}]})
        assert res.status_code == 401

    def test_create_order_empty_items_rejected(self, client, user_headers):
        res = client.post("/api/orders", headers=user_headers, json={"items": []})
        assert res.status_code == 422

    def test_create_order_unknown_product(self, client, user_headers):
        res = client.post("/api/orders", headers=user_headers, json={"items": [{"product_id": 9999}]})
        assert res.status_code == 404

    def test_order_lifecycle_get_after_create(self, client, user_headers):
        created = client.post(
            "/api/orders",
            headers=user_headers,
            json={"items": [{"product_id": 3, "quantity": 1}]},
        ).json()
        fetched = client.get(f"/api/orders/{created['id']}", headers=user_headers)
        assert fetched.status_code == 200
        body = fetched.json()
        assert body["id"] == created["id"]
        assert body["total"] == created["total"]

    def test_cannot_read_other_users_order(self, client, user_token, admin_token):
        created = client.post(
            "/api/orders",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"items": [{"product_id": 5, "quantity": 1}]},
        ).json()
        res = client.get(
            f"/api/orders/{created['id']}",
            headers={
                "Authorization": f"Bearer {client.post('/api/auth/login', json={'username': 'admin', 'password': 'admin1234'}).json()['access_token']}"
            },
        )
        assert res.status_code == 200

    def test_stock_decremented_after_order(self, client, user_headers):
        before = client.get("/api/products/7").json()["stock"]
        qty = 1
        client.post("/api/orders", headers=user_headers, json={"items": [{"product_id": 7, "quantity": qty}]})
        after = client.get("/api/products/7").json()["stock"]
        assert after == before - qty
