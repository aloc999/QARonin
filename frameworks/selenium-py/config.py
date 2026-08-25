import os

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8199")
BROWSER = os.environ.get("BROWSER", "chrome")
HEADLESS = os.environ.get("HEADLESS", "1") != "0"
SELENIUM_REMOTE_URL = os.environ.get("SELENIUM_REMOTE_URL")

DEMO_USER = ("demo", "demo1234")
ADMIN_USER = ("admin", "admin1234")
