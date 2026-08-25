"""Capabilities factory for Android (UiAutomator2) sessions."""

import os


def android_caps(
    app_path: str | None = None,
    device_name: str | None = None,
    platform_version: str | None = None,
    app_package: str | None = None,
    app_activity: str | None = None,
    no_reset: bool = False,
) -> dict:
    app_path = app_path or os.environ.get("APPIUM_APP_PATH", "")
    return {
        "platformName": "Android",
        "appium:automationName": "UiAutomator2",
        "appium:deviceName": device_name or os.environ.get("APPIUM_DEVICE_NAME", "emulator-5554"),
        "appium:platformVersion": platform_version or os.environ.get("APPIUM_PLATFORM_VERSION"),
        **({"appium:app": os.path.abspath(app_path)} if app_path else {}),
        **({"appium:appPackage": app_package or os.environ.get("APPIUM_APP_PACKAGE")} if (app_package or os.environ.get("APPIUM_APP_PACKAGE")) else {}),
        **({"appium:appActivity": app_activity or os.environ.get("APPIUM_APP_ACTIVITY")} if (app_activity or os.environ.get("APPIUM_APP_ACTIVITY")) else {}),
        "appium:newCommandTimeout": 120,
        "appium:autoGrantPermissions": True,
        "appium:noReset": no_reset,
        "appium:ensureWebviewsHavePages": True,
        "appium:nativeWebScreenshot": True,
    }


def webdriverio_demo_app_caps(app_path: str, no_reset: bool = False) -> dict:
    """Capabilities for the WebdriverIO demo app (wdio-native-app-demo).

    APK: https://github.com/webdriverio/native-demo-app/releases
    (android-*.apk). CI downloads the latest release asset; locally set
    APPIUM_APP_PATH to the downloaded file.
    """
    return android_caps(
        app_path=app_path,
        app_package="com.wdiodemoapp",
        app_activity=".MainActivity",
        no_reset=no_reset,
    )
