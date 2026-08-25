"""Screen-object locator tables for the WebdriverIO native demo app.

Selectors target the wdio-native-app-demo APK
(https://github.com/webdriverio/native-demo-app/releases). Accessibility ids
are stable across releases; resource-ids are kept as fallbacks.
"""

LOGIN_SCREEN = {
    "username_input": {"accessibility_id": "input-email"},
    "password_input": {"accessibility_id": "input-password"},
    "login_button": {"accessibility_id": "button-login-container"},
    "login_tab": {"accessibility_id": "button-login-container"},
}

HOME_SCREEN = {
    "webview_card_title": {
        "xpath": '//android.widget.TextView[@text="WebView"]'
    },
    "login_nav": {"accessibility_id": "button-login-container"},
    "drag_nav": {"accessibility_id": "button-drag-container"},
}

CATALOG_SCREEN = {
    "catalog_title": {
        "xpath": '//android.widget.TextView[@text="Products"]'
    },
    "product_cards": {
        "xpath": '//android.view.ViewGroup[@content-desc="store-item"]'
    },
    "first_product_name": {
        "xpath": '(//android.view.ViewGroup[@content-desc="store-item"]//android.widget.TextView)[1]'
    },
}

CART_SCREEN = {
    "cart_icon": {"accessibility_id": "cart-tab"},
    "cart_badge": {
        "xpath": '//android.view.ViewGroup[@content-desc="cart-tab"]//android.widget.TextView'
    },
    "checkout_button": {"accessibility_id": "Proceed To Checkout Button"},
    "cart_items": {"xpath": '//android.widget.ScrollView//*[contains(@content-desc, "store item")]'},
}
