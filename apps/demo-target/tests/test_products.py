class TestProductReads:
    def test_list_products_seeded_eight(self, client):
        res = client.get("/api/products")
        assert res.status_code == 200
        products = res.json()
        assert len(products) == 8
        for p in products:
            assert isinstance(p["id"], int)
            assert isinstance(p["name"], str) and p["name"]
            assert isinstance(p["price"], (int, float)) and p["price"] > 0
            assert isinstance(p["stock"], int) and p["stock"] >= 0

    def test_get_product_by_id(self, client):
        res = client.get("/api/products/1")
        assert res.status_code == 200
        p = res.json()
        assert p["id"] == 1
        assert "description" in p

    def test_get_product_not_found(self, client):
        res = client.get("/api/products/9999")
        assert res.status_code == 404
        assert res.json()["detail"] == "Product not found"

    def test_get_product_invalid_id_type(self, client):
        res = client.get("/api/products/not-a-number")
        assert res.status_code == 422
