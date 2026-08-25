from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class ProductsPage(BasePage):
    path = "/products"

    PRODUCT_CARDS = (By.CSS_SELECTOR, ".card.product")
    ADD_BUTTON_IN_CARD = (By.CSS_SELECTOR, ".add-to-cart")
    FLASH = (By.ID, "flash")

    def card_count(self) -> int:
        return len(self.driver.find_elements(*self.PRODUCT_CARDS))

    def wait_product_count(self, count: int) -> bool:
        return self.wait.count_is(By.CSS_SELECTOR, ".card.product", count)

    def card_for(self, product_name: str):
        cards = self.driver.find_elements(*self.PRODUCT_CARDS)
        for card in cards:
            if product_name in card.find_element(By.TAG_NAME, "h3").text:
                return card
        raise AssertionError(f"No product card containing {product_name!r}")

    def add_to_cart(self, product_name: str):
        card = self.card_for(product_name)
        card.find_element(*self.ADD_BUTTON_IN_CARD).click()
        self.wait.visible(self.FLASH)

    def flash_text(self) -> str:
        return self.wait.visible(self.FLASH).text
