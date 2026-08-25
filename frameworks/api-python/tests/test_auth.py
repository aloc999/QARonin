import pytest


@pytest.mark.smoke
class TestAuth:
    def test_login_success_returns_token(self, api):
        res = api.post("/api/auth/login", json={"username": "demo", "password": "demo1234"})
        assert res.status_code == 200
        body = res.json()
        assert body["token_type"] == "bearer"
        assert isinstance(body["access_token"], str) and len(body["access_token"]) > 20

    def test_login_rejects_wrong_password(self, api):
        res = api.post("/api/auth/login", json={"username": "demo", "password": "bad"})
        assert res.status_code == 401

    def test_login_rejects_unknown_user(self, api):
        res = api.post("/api/auth/login", json={"username": "nobody", "password": "x"})
        assert res.status_code == 401

    def test_login_validation_error(self, api):
        res = api.post("/api/auth/login", json={})
        assert res.status_code == 422

    @pytest.mark.regression
    def test_token_is_two_part_hmac(self, api):
        token = api.post("/api/auth/login", json={"username": "demo", "password": "demo1234"}).json()["access_token"]
        parts = token.split(".")
        assert len(parts) == 2
        assert all(len(p) > 10 for p in parts)
