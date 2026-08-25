"""Driver/session fixtures.

The whole module is gated by RUN_APPIUM=1: without it every mobile test is
skipped with a clear reason so `pytest` exits 0 on any machine.
"""

import os

import pytest

from caps.android_caps import webdriverio_demo_app_caps
from pages.cart_screen import CartScreen
from pages.catalog_screen import CatalogScreen
from pages.login_screen import LoginScreen
from utils.mobile_wait import MobileWait


def pytest_collection_modifyitems(config, items):
    gate = os.environ.get("RUN_APPIUM") != "1"
    if not gate:
        return
    skip_marker = pytest.mark.skip(
        reason="RUN_APPIUM!=1: set RUN_APPIUM=1 with a running Appium server "
               "and Android emulator to execute mobile tests"
    )
    for item in items:
        if "mobile" in item.keywords:
            item.add_marker(skip_marker)


@pytest.fixture(scope="session")
def driver():
    if os.environ.get("RUN_APPIUM") != "1":
        pytest.skip("RUN_APPIUM!=1")
    from appium import webdriver
    from appium.options.android import UiAutomator2Options
    from appium.webdriver.common.appiumby import AppiumBy  # noqa: F401

    app_path = os.environ.get("APPIUM_APP_PATH", "")
    options = UiAutomator2Options().load_capabilities(
        webdriverio_demo_app_caps(app_path or None)
    )
    driver = webdriver.Remote(
        os.environ.get("APPIUM_SERVER_URL", "http://127.0.0.1:4723"),
        options=options,
    )
    yield driver
    driver.quit()


@pytest.fixture
def wait(driver):
    return MobileWait(driver)


@pytest.fixture
def login_screen(driver, wait):
    return LoginScreen(driver, wait)


@pytest.fixture
def catalog_screen(driver, wait):
    return CatalogScreen(driver, wait)


@pytest.fixture
def cart_screen(driver, wait):
    return CartScreen(driver, wait)
