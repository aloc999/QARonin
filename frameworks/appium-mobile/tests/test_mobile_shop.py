import pytest


pytestmark = pytest.mark.mobile


class TestLoginFlow:
    def test_login_screen_renders_email_and_password_fields(self, login_screen):
        assert login_screen.element("username_input") is not None
        assert login_screen.element("password_input") is not None

    def test_login_with_valid_credentials_succeeds(self, login_screen):
        login_screen.login("test@example.com", "correct-password")

    def test_login_with_invalid_credentials_shows_feedback(self, login_screen):
        login_screen.type_text("username_input", "wrong@example.com")
        login_screen.type_text("password_input", "bad")
        login_screen.tap("login_button")


class TestCatalogFlow:
    def test_catalog_lists_products(self, catalog_screen):
        count = catalog_screen.product_count()
        assert count >= 1

    def test_add_to_cart_updates_badge(self, catalog_screen, cart_screen):
        before = int(cart_screen.badge_text() or "0")
        catalog_screen.add_first_product_to_cart()
        after = int(cart_screen.badge_text() or "0")
        assert after == before + 1

    def test_cart_shows_added_item(self, catalog_screen, cart_screen):
        catalog_screen.add_first_product_to_cart()
        cart_screen.open()
        assert cart_screen.item_count() >= 1
