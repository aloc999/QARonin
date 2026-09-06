"""Explicit-wait helper for mobile screens; no blind sleeps."""

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

DEFAULT_TIMEOUT = 20


class MobileWait:
    def __init__(self, driver, timeout: int = DEFAULT_TIMEOUT):
        self.wait = WebDriverWait(driver, timeout, poll_frequency=0.5)

    def visible(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def clickable(self, locator):
        return self.wait.until(EC.element_to_be_clickable(locator))

    def present(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))
