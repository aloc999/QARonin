from pages.base_screen import BaseScreen
from pages.locators import LOGIN_SCREEN


class LoginScreen(BaseScreen):
    LOCATORS = LOGIN_SCREEN

    def login(self, username: str, password: str):
        self.type_text("username_input", username)
        self.type_text("password_input", password)
        self.tap("login_button")

    def error_text(self) -> str:
        return ""
