# Traceability Matrix (QMS-TM-001, v1.0)

Requirement -> test cases -> automation. AE = automationexercise.com/test_cases.

| Req ID | Requirement (RoninShop) | AE analogue | Automated coverage |
|--------|-------------------------|-------------|--------------------|
| REQ-AUTH-01 | Login with valid credentials | AE-2 | api-python test_auth, Karate auth.feature, Pact login, PW-TS smoke, PW-C# smoke |
| REQ-AUTH-02 | Login with invalid credentials shows error | AE-3 | api-python 401 case, PW-TS smoke invalid-login, PW-C# parity, AE parity test |
| REQ-AUTH-03 | Logout clears session | AE-4 | PW-TS regression logout, PW-C# parity, AE parity test |
| REQ-AUTH-04 | Existing user cannot re-register / duplicate handled | AE-5 | api-python RBAC/seed tests, AE live check |
| REQ-CAT-01 | Product list visible | AE-8 | api-python test_products, Karate products.feature, Pact list, PW smoke grid |
| REQ-CAT-02 | Product detail shows name/price/stock | AE-8 | api-python detail, Karate detail, Pact get-one, AE parity |
| REQ-CAT-03 | Search products | AE-9, AE-20 | AE live check + parity note (RoninShop search out of scope -> recorded gap) |
| REQ-CART-01 | Add products to cart, badge increments | AE-12 | PW-TS smoke add-to-cart, Selenium parity, AE parity |
| REQ-CART-02 | Cart quantity handling | AE-13 | PW-TS regression cart-persist, AE parity |
| REQ-CART-03 | Remove product from cart | AE-17 | AE parity (localStorage cart clear), Selenium |
| REQ-ORDER-01 | Place order (register-while-checkout flow) | AE-14 | api-python test_orders, Karate orders.feature, Pact create-order, PW e2e-purchase |
| REQ-ORDER-02 | Place order (login-before-checkout) | AE-16 | PW e2e-purchase, api-python orders |
| REQ-ORDER-03 | Order RBAC: users see own orders only | — | api-python test_rbac, Karate RBAC, db-validation RBAC-vs-DB |
| REQ-ORDER-04 | Admin sees all orders | — | api-python admin, Pact (admin via api), db-validation |
| REQ-REVIEW-01 | Product review | AE-21 | AE live check only (RoninShop reviews out of scope -> gap) |
| REQ-SUB-01 | Subscription/footer | AE-10, AE-11 | AE live check only (gap) |
| REQ-SCROLL-01 | Scroll up/down | AE-25, AE-26 | AE live check only (gap) |
| REQ-OBS-01 | Health + metrics endpoints | — | observability tests |
| REQ-CONTRACT-01 | Consumer-driven contracts hold | — | Pact consumer+provider |
| REQ-PERF-01 | Checkout p95 < 1200ms, reads p95 < 800ms | — | k6 SLO gates, Locust profile |

Gaps (no RoninShop analogue) are intentional scope records, not failures.
Full 26-case AE mapping with steps lives in frameworks/automationexercise/README.md.
