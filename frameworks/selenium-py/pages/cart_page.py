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
        # Explicit wait first: raw find_elements would race table render.
        self.wait.present(self.CART_ROWS)
        return len(self.driver.find_elements(*self.CART_ROWS))

    def wait_row_count(self, count: int):
        self.wait.count_is(By.CSS_SELECTOR, "#cart-table tbody tr.cart-row", count)

    def total_text(self) -> str:
        return self.wait.visible(self.CART_TOTAL).text

    def checkout(self):
        self.wait.clickable(self.PLACE_ORDER).click()

    def order_id_text(self) -> str:
        # Order round-trip (POST + re-render) gets a 30s conditional wait:
        # twice timed out on loaded CI runners at the default 10s, never locally.
        text = self.wait.with_timeout(30).visible(self.ORDER_ID).text
        assert text.startswith("#") and text[1:].isdigit()
        return text
