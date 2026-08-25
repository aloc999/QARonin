"""Shared pytest fixtures: WebDriver session, page objects."""

import os

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService

from config import BASE_URL, BROWSER, HEADLESS, SELENIUM_REMOTE_URL
from pages.login_page import LoginPage
from pages.products_page import ProductsPage
from pages.cart_page import CartPage


def _service(env_var: str):
    """Optional explicit driver binary via env; falls back to Selenium Manager."""
    path = os.environ.get(env_var)
    if BROWSER == "firefox":
        return FirefoxService(path) if path else None
    return ChromeService(path) if path else None


def _local_options():
    if BROWSER == "firefox":
        options = FirefoxOptions()
    else:
        options = ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
    if HEADLESS:
        if BROWSER == "firefox":
            options.add_argument("-headless")
        else:
            options.add_argument("--headless=new")
    return options


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture
def driver():
    if SELENIUM_REMOTE_URL:
        driver = webdriver.Remote(
            command_executor=SELENIUM_REMOTE_URL,
            options=_local_options(),
        )
    else:
        if BROWSER == "firefox":
            service = _service("GECKODRIVER_PATH")
            driver = webdriver.Firefox(options=_local_options(), service=service)
        else:
            service = _service("CHROMEDRIVER_PATH")
            driver = webdriver.Chrome(options=_local_options(), service=service)
    driver.set_page_load_timeout(30)
    yield driver
    driver.quit()


@pytest.fixture
def login_page(driver, base_url):
    page = LoginPage(driver, base_url)
    page.open()
    return page


@pytest.fixture
def products_page(driver, base_url):
    page = ProductsPage(driver, base_url)
    page.open()
    return page


@pytest.fixture
def cart_page(driver, base_url):
    page = CartPage(driver, base_url)
    return page
