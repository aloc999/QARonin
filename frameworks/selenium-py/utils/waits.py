"""Explicit-wait helper. All waits are conditional; no blind sleeps."""

from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

DEFAULT_TIMEOUT = 10


class Wait:
    def __init__(self, driver: WebDriver, timeout: int = DEFAULT_TIMEOUT):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout, poll_frequency=0.2)

    def with_timeout(self, seconds: int) -> "Wait":
        """Longer leash for multi-round-trip flows (e.g. order checkout on
        loaded CI runners). Still conditional, never a fixed sleep."""
        return Wait(self.driver, seconds)

    def visible(self, locator: tuple[str, str]):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def clickable(self, locator: tuple[str, str]):
        return self.wait.until(EC.element_to_be_clickable(locator))

    def present(self, locator: tuple[str, str]):
        return self.wait.until(EC.presence_of_element_located(locator))

    def invisible(self, locator: tuple[str, str]):
        try:
            return self.wait.until(EC.invisibility_of_element_located(locator))
        except TimeoutException:
            return False

    def text_is(self, locator: tuple[str, str], expected: str) -> bool:
        def _match(driver):
            try:
                el = driver.find_element(*locator)
                return el.text == expected
            except StaleElementReferenceException:
                return False
        try:
            self.wait.until(_match)
            return True
        except TimeoutException:
            actual = ""
            try:
                actual = self.driver.find_element(*locator).text
            except Exception:
                pass
            raise AssertionError(
                f"Element {locator} text did not become {expected!r}; last value {actual!r}"
            )

    def count_is(self, by: By, selector: str, expected: int) -> bool:
        def _match(driver):
            return len(driver.find_elements(by, selector)) == expected
        self.wait.until(_match)
        return True

    def url_matches(self, pattern: str) -> bool:
        return self.wait.until(lambda d: pattern in d.current_url)
