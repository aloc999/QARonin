# Appium Mobile Framework

Mobile automation skeleton with real test logic against the open-source
[WebdriverIO native demo app](https://github.com/webdriverio/native-demo-app)
(`com.wdiodemoapp`, Android, UiAutomator2).

## Execution gate

Every mobile test requires `RUN_APPIUM=1`, a running Appium 2.x server
(`npm i -g appium && appium driver install uiautomator2`) and a booted Android
emulator. Without `RUN_APPIUM=1` all device tests skip with an explicit
reason, so `pytest` collects and exits 0 on any machine (CI included).
The caps builder and screen-object locator tables are unit-tested without a
device in `tests/test_caps_and_screens.py`.

## Layout

```
appium-mobile/
├── caps/android_caps.py   capabilities factory (UiAutomator2, app path/package
│                          via args or APPIUM_* env vars) + wdio demo-app preset
├── pages/                 LoginScreen / CatalogScreen / CartScreen over a shared
│                          BaseScreen + locator tables in pages/locators.py
├── utils/mobile_wait.py   explicit-wait helper, no blind sleeps
└── tests/
    ├── test_caps_and_screens.py   device-free unit tests (always run)
    └── test_mobile_shop.py        6 @mobile tests: login render/valid/invalid,
                                    catalog list, add-to-cart badge, cart contents
```

## Environment variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `RUN_APPIUM` | unset | Must be `1` to execute device tests |
| `APPIUM_SERVER_URL` | `http://127.0.0.1:4723` | Appium server endpoint |
| `APPIUM_APP_PATH` | unset | Path to the APK; CI downloads the latest wdio demo release |
| `APPIUM_DEVICE_NAME` | `emulator-5554` | Device/AVD name |
| `APPIUM_PLATFORM_VERSION` | auto | Android version |
| `APPIUM_APP_PACKAGE` / `APPIUM_APP_ACTIVITY` | unset | Override launch target |

## Running locally

```bash
pip install -r requirements.txt
# download APK from https://github.com/webdriverio/native-demo-app/releases
export RUN_APPIUM=1 APPIUM_APP_PATH=/path/to/android-*.apk
pytest -v
```

## CI

`.github/workflows/mobile.yml` boots an Android emulator on an ubuntu runner,
installs Appium server via npm, downloads the latest demo APK and runs the
suite with `RUN_APPIUM=1`; failure artifacts are uploaded.
