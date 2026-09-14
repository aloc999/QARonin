"""RBAC-vs-database contract: the users.role column must predict API behavior.

Complements test_validators.py (which checks one known pair): every row in
users is exercised against /api/admin/orders, so a seed/RBAC drift fails here
first. Needs the live demo target (BASE_URL, default 127.0.0.1:8199).
"""

import os

import requests
from sqlalchemy import text

from dbval.connection import make_session_factory, create_db_engine

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8199")
PASSWORDS = {"demo": "demo1234", "admin": "admin1234"}


def _roles():
    session = make_session_factory(create_db_engine())()
    try:
        return dict(session.execute(text("SELECT username, role FROM users")).fetchall())
    finally:
        session.close()


def _token(username):
    res = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": username, "password": PASSWORDS[username]},
        timeout=10,
    )
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


def test_users_table_has_expected_roles():
    assert _roles() == {"demo": "user", "admin": "admin"}


def test_non_admin_rows_denied_admin_endpoint():
    for username, role in _roles().items():
        if role == "admin" or username not in PASSWORDS:
            continue
        res = requests.get(
            f"{BASE_URL}/api/admin/orders",
            headers={"Authorization": f"Bearer {_token(username)}"},
            timeout=10,
        )
        assert res.status_code == 403, f"{username} with db role {role!r} reached admin endpoint"


def test_admin_row_allowed_and_count_matches_db():
    admins = [u for u, r in _roles().items() if r == "admin"]
    assert admins, "no admin row in users table"
    res = requests.get(
        f"{BASE_URL}/api/admin/orders",
        headers={"Authorization": f"Bearer {_token(admins[0])}"},
        timeout=10,
    )
    assert res.status_code == 200
    session = make_session_factory(create_db_engine())()
    try:
        db_count = session.execute(text("SELECT COUNT(*) FROM orders")).scalar()
    finally:
        session.close()
    assert res.json()["count"] == db_count
