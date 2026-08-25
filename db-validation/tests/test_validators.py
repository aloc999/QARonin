import os

import pytest
import requests
from sqlalchemy import text

from dbval.connection import create_db_engine, database_url, make_session_factory

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8199")


@pytest.fixture(scope="session")
def engine():
    return create_db_engine()


@pytest.fixture(scope="session")
def session_factory(engine):
    return make_session_factory(engine)


@pytest.fixture(scope="session")
def api_order(session_factory):
    """Create one order through the public API and return its payload."""
    login = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": "demo", "password": "demo1234"},
    )
    token = login.json()["access_token"]
    resp = requests.post(
        f"{BASE_URL}/api/orders",
        json={"items": [{"product_id": 2, "quantity": 2}]},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201, resp.text
    order = resp.json()
    yield order


def test_api_order_row_matches_line_items(api_order, session_factory):
    session = session_factory()
    row = session.execute(
        text("SELECT username, total, status FROM orders WHERE id = :id"),
        {"id": api_order["id"]},
    ).fetchone()
    assert row is not None, f"API order {api_order['id']} missing in DB"
    assert row.username == "demo"
    assert row.status == "confirmed"

    expected = sum(i["quantity"] * i["unit_price"] for i in api_order["items"])
    assert abs(row.total - expected) < 0.005

    items = session.execute(
        text("""SELECT product_id, quantity, unit_price FROM order_items
                WHERE order_id = :id"""),
        {"id": api_order["id"]},
    ).fetchall()
    assert [(i.product_id, i.quantity, float(i.unit_price)) for i in items] == [
        (i["product_id"], i["quantity"], i["unit_price"])
        for i in api_order["items"]
    ]
    session.close()


def test_order_integrity_no_violations(session_factory):
    from dbval.validators import order_integrity

    session = session_factory()
    violations = order_integrity(session)
    assert violations == [], "\n".join(violations)
    session.close()


def test_referential_integrity_no_orphans(session_factory):
    from dbval.validators import referential_integrity

    session = session_factory()
    assert referential_integrity(session) == []
    session.close()


def test_seeded_data_quality(session_factory):
    from dbval.validators import seeded_data_quality

    session = session_factory()
    assert seeded_data_quality(session) == []
    session.close()


def test_rbac_enforcement_db_flag_matches_api(session_factory):
    """The users.role column must predict API behavior exactly."""
    session = session_factory()
    roles = dict(
        session.execute(text("SELECT username, role FROM users")).fetchall()
    )
    session.close()

    for username, role in roles.items():
        password = {
            "demo": "demo1234",
            "admin": "admin1234",
        }.get(username)
        if password is None:
            continue
        login = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": username, "password": password},
        )
        token = login.json()["access_token"]
        resp = requests.get(
            f"{BASE_URL}/api/admin/orders",
            headers={"Authorization": f"Bearer {token}"},
        )
        if role == "admin":
            assert resp.status_code == 200
        else:
            assert resp.status_code == 403
        assert roles[username] == role


def test_assert_query_helper_scalar_and_rows(session_factory):
    from dbval.assert_query import assert_query

    session = session_factory()
    count = session.execute(text("SELECT COUNT(*) FROM products")).scalar()
    assert_query(session, "SELECT COUNT(*) FROM products", int(count))
    assert_query(session, "SELECT username FROM users ORDER BY id LIMIT 1", "demo")
    session.close()


def test_snapshot_diff_detects_mutation(engine, session_factory):
    from dbval.snapshot import assert_no_unexpected_mutation, db_snapshot, diff_snapshots

    before = db_snapshot(engine)
    after = db_snapshot(engine)
    d = diff_snapshots(before, after)
    assert d["changed_counts"] == {}
    assert d["mutated_rows"] == {}

    session = session_factory()
    try:
        session.execute(text(
            "INSERT INTO products (name, description, price, stock) "
            "VALUES ('__snapshot_probe__', '', 1.0, 1)"
        ))
        session.commit()
        try:
            after_inserted = db_snapshot(engine)
            with pytest.raises(AssertionError):
                assert_no_unexpected_mutation(before, after_inserted)
        finally:
            session.execute(
                text("DELETE FROM products WHERE name = '__snapshot_probe__'")
            )
            session.commit()
    finally:
        session.close()
    restored = diff_snapshots(before, db_snapshot(engine))
    assert restored["changed_counts"] == {}
    assert restored["mutated_rows"] == {}
