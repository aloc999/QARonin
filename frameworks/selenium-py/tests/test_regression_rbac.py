import pytest
import requests

from config import ADMIN_USER, DEMO_USER, BASE_URL
from pages.login_page import LoginPage


@pytest.mark.regression
class TestRbacRegression:
    def test_admin_denial_shows_error_for_regular_user(self, driver, base_url):
        login = LoginPage(driver, base_url)
        login.open()
        login.login_and_expect_products(*DEMO_USER)
        token = driver.execute_script("return localStorage.getItem('token');")
        assert token

        result = driver.execute_async_script(
            """
            const done = arguments[arguments.length - 1];
            fetch(arguments[0] + '/api/admin/orders', {
                headers: { Authorization: 'Bearer ' + arguments[1] }
            })
                .then(async (res) => done({ status: res.status, body: await res.json() }))
                .catch((e) => done({ error: String(e) }));
            """,
            base_url,
            token,
        )
        assert result["status"] == 403
        assert result["body"]["detail"] == "Admin role required"

    def test_admin_role_in_api_allows_admin_endpoint(self, driver, base_url):
        resp = requests.post(
            f"{base_url}/api/auth/login",
            json={"username": ADMIN_USER[0], "password": ADMIN_USER[1]},
        )
        admin_token = resp.json()["access_token"]
        result = requests.get(
            f"{base_url}/api/admin/orders",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert result.status_code == 200
        assert "orders" in result.json()
