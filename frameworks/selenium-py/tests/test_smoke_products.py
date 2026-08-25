import pytest

from config import DEMO_USER
from pages.products_page import ProductsPage


@pytest.mark.smoke
class TestProductsSmoke:
    def test_products_grid_loads_seeded_catalog(self, products_page):
        assert products_page.wait_product_count(8)
        card = products_page.driver.find_element(*products_page.PRODUCT_CARDS)
        assert "$" in card.text

    def test_add_to_cart_increments_badge(self, login_page):
        login_page.login_and_expect_products(*DEMO_USER)
        products = ProductsPage(login_page.driver, login_page.base_url)
        before = int(products.cart_count_text() or "0")
        products.add_to_cart("Ronin Tea Set")
        after = int(products.cart_count_text())
        assert after == before + 1
        assert products.flash_text() == "Ronin Tea Set added to cart."
