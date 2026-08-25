import pytest


@pytest.mark.regression
class TestRbac:
    def test_user_token_cannot_access_admin(self, api, auth_headers):
        res = api.get("/api/admin/orders", headers=auth_headers)
        assert res.status_code == 403
        assert res.json()["detail"] == "Admin role required"

    def test_admin_token_can_access_admin(self, api, admin_headers):
        res = api.get("/api/admin/orders", headers=admin_headers)
        assert res.status_code == 200
        assert "count" in res.json()

    def test_missing_token_is_401(self, api):
        assert api.get("/api/admin/orders").status_code == 401

    def test_garbage_token_is_401(self, api):
        res = api.get("/api/admin/orders", headers={"Authorization": "Bearer not.a.token"})
        assert res.status_code == 401

    def test_role_field_reflected_in_login(self, api):
        user = api.post("/api/auth/login", json={"username": "demo", "password": "demo1234"}).json()
        admin = api.post("/api/auth/login", json={"username": "admin", "password": "admin1234"}).json()
        assert user["role"] == "user"
        assert admin["role"] == "admin"
