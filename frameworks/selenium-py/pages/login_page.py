from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from pages.base_page import BasePage


class LoginPage(BasePage):
    path = "/login"

    USERNAME = (By.ID, "username")
    PASSWORD = (By.ID, "password")
    SUBMIT = (By.CSS_SELECTOR, "#login-form button[type=submit]")
    ERROR_BOX = (By.ID, "login-error")

    def enter_username(self, username: str):
        box = self.wait.visible(self.USERNAME)
        box.clear()
        box.send_keys(username)

    def enter_password(self, password: str):
        box = self.wait.visible(self.PASSWORD)
        box.clear()
        box.send_keys(password)

    def submit(self):
        self.wait.clickable(self.SUBMIT).click()

    def login(self, username: str, password: str):
        self.enter_username(username)
        self.enter_password(password)
        self.submit()

    def login_and_expect_products(self, username: str, password: str):
        self.login(username, password)
        self.wait.url_matches("/products")

    def error_text(self) -> str:
        return self.wait.visible(self.ERROR_BOX).text

    def press_enter_in_password(self):
        self.wait.visible(self.PASSWORD).send_keys(Keys.ENTER)
