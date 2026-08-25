from selenium.webdriver.common.by import By


class BasePage:
    path = "/"

    def __init__(self, driver, base_url: str):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.waiter = None

    @property
    def wait(self):
        if self.waiter is None:
            from utils.waits import Wait
            self.waiter = Wait(self.driver)
        return self.waiter

    def open(self, path: str | None = None):
        self.driver.get(f"{self.base_url}{path or self.path}")
        return self

    CART_COUNT = (By.ID, "cart-count")
    USER_BADGE = (By.ID, "user-badge")
    LOGOUT_BUTTON = (By.ID, "logout-btn")

    def cart_count_text(self) -> str:
        return self.wait.visible(self.CART_COUNT).text

    def user_badge_text(self) -> str:
        return self.wait.present(self.USER_BADGE).text

    def logout(self):
        self.wait.clickable(self.LOGOUT_BUTTON).click()
