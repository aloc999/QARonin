from appium.webdriver.common.appiumby import AppiumBy

from pages.base_screen import BaseScreen
from pages.locators import CATALOG_SCREEN


class CatalogScreen(BaseScreen):
    LOCATORS = CATALOG_SCREEN

    ADD_BUTTON_IN_CARD = (
        AppiumBy.XPATH,
        '(//android.view.ViewGroup[@content-desc="store-item"]'
        '//*[contains(@content-desc, "Add")])[1]',
    )

    def product_count(self) -> int:
        return len(self.elements("product_cards"))

    def first_product_name(self) -> str:
        return self.element("first_product_name").text

    def add_first_product_to_cart(self):
        cards = self.elements("product_cards")
        assert cards, "no product cards rendered"
        buttons = cards[0].find_elements(*self.ADD_BUTTON_IN_CARD)
        assert buttons, "add-to-cart button not found in product card"
        buttons[0].click()
