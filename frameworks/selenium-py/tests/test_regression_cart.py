import pytest

from config import DEMO_USER
from pages.cart_page import CartPage
from pages.login_page import LoginPage
from pages.products_page import ProductsPage


@pytest.mark.regression
class TestCartRegression:
    def test_add_to_cart_updates_count_and_persists_across_refresh(
        self, driver, base_url
    ):
        login = LoginPage(driver, base_url)
        login.open()
        login.login_and_expect_products(*DEMO_USER)

        products = ProductsPage(driver, base_url)
        products.add_to_cart("Zen Garden Starter Kit")
        assert int(products.cart_count_text()) >= 1

        driver.refresh()
        refreshed = ProductsPage(driver, base_url)
        count = int(refreshed.cart_count_text() or "0")
        assert count >= 1, "cart badge lost after refresh"

        cart = CartPage(driver, base_url)
        cart.open()
        cart.wait_row_count(1)
        assert "$29.50" in cart.total_text()

    def test_checkout_creates_order_confirmation(self, driver, base_url):
        login = LoginPage(driver, base_url)
        login.open()
        login.login_and_expect_products(*DEMO_USER)

        products = ProductsPage(driver, base_url)
        products.add_to_cart("Origami Paper Pack")

        cart = CartPage(driver, base_url)
        cart.open()
        cart.checkout()
        order_id = cart.order_id_text()
        assert order_id.startswith("#")

        token = driver.execute_script("return localStorage.getItem('token');")
        assert token is not None
