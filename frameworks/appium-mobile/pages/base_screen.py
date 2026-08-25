from appium.webdriver.common.appiumby import AppiumBy

LOCATOR_TYPES = {
    "accessibility_id": AppiumBy.ACCESSIBILITY_ID,
    "id": AppiumBy.ID,
    "xpath": AppiumBy.XPATH,
    "css": AppiumBy.CSS_SELECTOR,
    "android_uiautomator": AppiumBy.ANDROID_UIAUTOMATOR,
}


class BaseScreen:
    LOCATORS: dict = {}

    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    def element(self, name: str):
        locator = self.LOCATORS[name]
        (by_type, value), = locator.items()
        return self.wait.visible((LOCATOR_TYPES[by_type], value))

    def elements(self, name: str):
        locator = self.LOCATORS[name]
        (by_type, value), = locator.items()
        return self.driver.find_elements(LOCATOR_TYPES[by_type], value)

    def tap(self, name: str):
        self.element(name).click()

    def type_text(self, name: str, text: str):
        field = self.element(name)
        field.clear()
        field.send_keys(text)
