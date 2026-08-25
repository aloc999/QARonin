import pytest


@pytest.mark.smoke
class TestProducts:
    def test_list_products_shape(self, api):
        res = api.get("/api/products")
        assert res.status_code == 200
        products = res.json()
        assert len(products) == 8
        required = {"id", "name", "description", "price", "stock"}
        for p in products:
            assert required.issubset(p.keys())
            assert isinstance(p["id"], int)
            assert isinstance(p["price"], (int, float))
            assert p["price"] > 0
            assert p["stock"] >= 0

    def test_get_single_product(self, api):
        res = api.get("/api/products/2")
        assert res.status_code == 200
        body = res.json()
        assert body["id"] == 2
        assert isinstance(body["name"], str) and body["name"]

    @pytest.mark.regression
    def test_missing_product_is_404(self, api):
        assert api.get("/api/products/424242").status_code == 404

    @pytest.mark.regression
    def test_invalid_id_format(self, api):
        assert api.get("/api/products/abc").status_code == 422

    @pytest.mark.regression
    def test_response_time_under_budget(self, api):
        import time

        start = time.monotonic()
        api.get("/api/products")
        elapsed = time.monotonic() - start
        assert elapsed < 2.0, f"products list took {elapsed:.3f}s, budget 2s"
