"""Unit tests for caps builder and screen locator tables (no device needed)."""

import os
import sys

from caps.android_caps import android_caps, webdriverio_demo_app_caps
from pages.cart_screen import CartScreen
from pages.catalog_screen import CatalogScreen
from pages.login_screen import LoginScreen
from pages.locators import CART_SCREEN, CATALOG_SCREEN, HOME_SCREEN, LOGIN_SCREEN

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestCapsBuilder:
    def test_defaults(self):
        caps = android_caps()
        assert caps["platformName"] == "Android"
        assert caps["appium:automationName"] == "UiAutomator2"
        assert caps["appium:deviceName"] == "emulator-5554"
        assert "appium:app" not in caps

    def test_explicit_values_override_env(self):
        caps = android_caps(
            app_path="/tmp/demo.apk",
            device_name="pixel-9",
            platform_version="15",
            app_package="com.example",
            app_activity=".Main",
            no_reset=True,
        )
        assert caps["appium:deviceName"] == "pixel-9"
        assert caps["appium:platformVersion"] == "15"
        assert caps["appium:appPackage"] == "com.example"
        assert caps["appium:appActivity"] == ".Main"
        assert caps["appium:noReset"] is True

    def test_app_path_made_absolute(self):
        caps = android_caps(app_path="relative/app.apk")
        assert os.path.isabs(caps["appium:app"])
        assert caps["appium:app"].endswith("app.apk")

    def test_wdio_demo_app_caps(self):
        caps = webdriverio_demo_app_caps("/x/app.apk")
        assert caps["appium:appPackage"] == "com.wdiodemoapp"
        assert caps["appium:appActivity"] == ".MainActivity"

    def test_env_overrides(self, monkeypatch):
        monkeypatch.setenv("APPIUM_DEVICE_NAME", "tablet-1")
        monkeypatch.setenv("APPIUM_APP_PACKAGE", "com.env.pkg")
        caps = android_caps()
        assert caps["appium:deviceName"] == "tablet-1"
        assert caps["appium:appPackage"] == "com.env.pkg"


class _FakeWait:
    def visible(self, locator):
        return ("visible", locator)


class _FakeDriver:
    def find_elements(self, by, value):
        return [("element", by, value)]


def _screen(screen_cls):
    return screen_cls(_FakeDriver(), _FakeWait())


class TestLocatorTables:
    def test_all_screens_have_locators(self):
        for table in (LOGIN_SCREEN, HOME_SCREEN, CATALOG_SCREEN, CART_SCREEN):
            assert table, "empty locator table"
            for name, locators in table.items():
                assert len(locators) == 1, f"{name} must have exactly one strategy"
                assert next(iter(locators)) in {
                    "accessibility_id", "id", "xpath", "css", "android_uiautomator"
                }

    def test_screen_objects_resolve_elements(self):
        login = _screen(LoginScreen)
        catalog = _screen(CatalogScreen)
        cart = _screen(CartScreen)
        assert login.element("username_input")[0] == "visible"
        assert catalog.element("first_product_name")[0] == "visible"
        assert cart.element("cart_badge")[0] == "visible"

    def test_catalog_add_button_locator_defined(self):
        from appium.webdriver.common.appiumby import AppiumBy

        by, value = CatalogScreen.ADD_BUTTON_IN_CARD
        assert by in (AppiumBy.XPATH, AppiumBy.ACCESSIBILITY_ID)
        assert value
