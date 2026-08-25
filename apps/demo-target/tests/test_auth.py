class TestLogin:
    def test_login_success(self, client):
        res = client.post("/api/auth/login", json={"username": "demo", "password": "demo1234"})
        assert res.status_code == 200
        body = res.json()
        assert body["token_type"] == "bearer"
        assert body["username"] == "demo"
        assert body["role"] == "user"
        assert len(body["access_token"].split(".")) == 2

    def test_login_admin_role(self, client):
        res = client.post("/api/auth/login", json={"username": "admin", "password": "admin1234"})
        assert res.status_code == 200
        assert res.json()["role"] == "admin"

    def test_login_wrong_password(self, client):
        res = client.post("/api/auth/login", json={"username": "demo", "password": "nope"})
        assert res.status_code == 401
        assert "Invalid credentials" in res.json()["detail"]

    def test_login_unknown_user(self, client):
        res = client.post("/api/auth/login", json={"username": "ghost", "password": "irrelevant"})
        assert res.status_code == 401

    def test_login_missing_fields(self, client):
        res = client.post("/api/auth/login", json={"username": "demo"})
        assert res.status_code == 422

    def test_tampered_token_rejected(self, client, user_token):
        tampered = user_token[:-4] + ("AAAA" if not user_token.endswith("AAAA") else "BBBB")
        res = client.get("/api/orders/1", headers={"Authorization": f"Bearer {tampered}"})
        assert res.status_code == 401
