from pages.base_screen import BaseScreen
from pages.locators import CART_SCREEN


class CartScreen(BaseScreen):
    LOCATORS = CART_SCREEN

    def open(self):
        self.tap("cart_icon")

    def badge_text(self) -> str:
        return self.element("cart_badge").text

    def item_count(self) -> int:
        return len(self.elements("cart_items"))

    def checkout(self):
        self.tap("checkout_button")
