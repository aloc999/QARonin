"""A05 Security Misconfiguration: hardening headers on every response.

The demo target ships a middleware that sets X-Content-Type-Options: nosniff
(see apps/demo-target/app/main.py); these tests pin it on API, UI, and
health endpoints so a regression (removed middleware) fails loudly.
"""

import pytest


@pytest.mark.smoke
@pytest.mark.parametrize("path", ["/api/health", "/api/products", "/products", "/login"])
def test_nosniff_header_present(api, path):
    res = api.get(path)
    assert res.status_code == 200
    assert res.headers.get("x-content-type-options") == "nosniff"
