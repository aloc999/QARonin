import pytest

from config import DEMO_USER


@pytest.mark.smoke
class TestLoginSmoke:
    def test_login_success_redirects_to_products(self, login_page):
        login_page.login_and_expect_products(*DEMO_USER)
        assert "products" in login_page.driver.current_url
        assert login_page.user_badge_text() == DEMO_USER[0]

    def test_login_invalid_credentials_shows_error(self, login_page):
        login_page.login("demo", "wrong-password")
        error = login_page.error_text()
        assert error == "Invalid username or password."

    def test_logout_clears_session(self, login_page, base_url, driver):
        login_page.login_and_expect_products(*DEMO_USER)
        login_page.logout()
        login_page.wait.url_matches("/login")
        token = driver.execute_script("return localStorage.getItem('token');")
        assert token is None
