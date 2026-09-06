from monitor import check


def _fake_fetch_ok(base, path, timeout=15):
    if path == "/api/health":
        return 200, b'{"status": "ok"}'
    if path == "/api/products":
        return 200, b'[{"id": 1, "name": "x", "price": 1.0, "stock": 2}]'
    return 200, b"<html>stable</html>"


def test_check_all_ok(monkeypatch):
    import monitor as m

    monkeypatch.setattr(m, "fetch", _fake_fetch_ok)
    out = check("http://x", {"min_products": 1, "required_keys": ["name", "price"],
                             "products_hash": "deadbeef"})
    by_name = {f["check"]: f for f in out}
    assert by_name["products-shape"]["ok"]
    assert by_name["products-hash"]["drift"] is True


def test_check_outage(monkeypatch):
    import monitor as m

    def boom(base, path, timeout=15):
        raise ConnectionError("down")

    monkeypatch.setattr(m, "fetch", boom)
    out = check("http://x", {})
    assert out == [{"check": "health", "ok": False, "detail": "down"}]
