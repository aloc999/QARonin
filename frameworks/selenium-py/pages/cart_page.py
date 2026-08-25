from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class CartPage(BasePage):
    path = "/cart"

    CART_ROWS = (By.CSS_SELECTOR, "#cart-table tbody tr.cart-row")
    CART_TOTAL = (By.ID, "cart-total")
    PLACE_ORDER = (By.ID, "place-order-btn")
    ORDER_ID = (By.ID, "order-id")
    ORDER_TOTAL = (By.ID, "order-total")
    CONFIRMATION = (By.ID, "order-confirmation")
    EMPTY_STATE = (By.ID, "cart-empty")

    def row_count(self) -> int:
        return len(self.driver.find_elements(*self.CART_ROWS))

    def wait_row_count(self, count: int):
        self.wait.count_is(By.CSS_SELECTOR, "#cart-table tbody tr.cart-row", count)

    def total_text(self) -> str:
        return self.wait.visible(self.CART_TOTAL).text

    def checkout(self):
        self.wait.clickable(self.PLACE_ORDER).click()

    def order_id_text(self) -> str:
        text = self.wait.visible(self.ORDER_ID).text
        assert text.startswith("#") and text[1:].isdigit()
        return text
