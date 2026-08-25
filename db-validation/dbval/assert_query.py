"""Reusable assertion helper."""

from sqlalchemy import text

from .connection import fetch_rows


def assert_query(session, query: str, expected, params: dict | None = None,
                 message: str = ""):
    """Assert that a SQL query returns exactly `expected`.

    - scalar query (single column, single row): pass a raw value
    - multi-row query: pass a list of tuples/lists
    """
    rows = fetch_rows(session, query, params)
    if rows and len(rows) == 1 and len(rows[0]) == 1 and not isinstance(
        expected, (list, tuple)
    ):
        actual = rows[0][0]
    else:
        actual = [tuple(r) for r in rows] if isinstance(expected, list) else rows
    assert actual == expected, message or (
        f"query {query!r} returned {actual!r}, expected {expected!r}"
    )


def scalar(session, query: str, params: dict | None = None):
    return session.execute(text(query), params or {}).scalar()


def run_query(session, query: str, params: dict | None = None):
    return fetch_rows(session, query, params)
