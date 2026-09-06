"""UI page rendering: every HTML route must return 200 on ANY supported
Starlette (old name-first and new request-first TemplateResponse API).

Regression test for the version-drift 500s: app/main.py _render() adapts
via signature inspection, and this suite fails the build if rendering
breaks again under a resolver upgrade.
"""


def test_login_page_renders(client):
    res = client.get("/login")
    assert res.status_code == 200
    assert "Sign in" in res.text


def test_products_page_renders_seeded_catalog(client):
    res = client.get("/products")
    assert res.status_code == 200
    assert res.text.count("card product") == 8
    assert "$" in res.text


def test_cart_page_renders(client):
    res = client.get("/cart")
    assert res.status_code == 200


def test_index_redirects_to_products(client):
    res = client.get("/", follow_redirects=False)
    assert res.status_code in (302, 307)
    assert res.headers["location"].endswith("/products")
