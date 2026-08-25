"""Snapshot + diff utility to detect unexpected mutations."""

from sqlalchemy import text

from .connection import create_db_engine, make_session_factory

_TABLES = ["users", "products", "orders", "order_items"]


def db_snapshot(engine=None) -> dict:
    """Capture a comparable snapshot: row counts per table plus per-table
    content digests (ordered rows as tuples)."""
    engine = engine or create_db_engine()
    factory = make_session_factory(engine)
    session = factory()
    try:
        snapshot: dict[str, dict] = {}
        for table in _TABLES:
            count = session.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            rows = session.execute(
                text(f"SELECT * FROM {table} ORDER BY 1")
            ).fetchall()
            snapshot[table] = {
                "count": int(count),
                "rows": [tuple(str(v) for v in row) for row in rows],
            }
        return snapshot
    finally:
        session.close()


def diff_snapshots(before: dict, after: dict) -> dict:
    """Return a dict of unexpected mutations between two snapshots.

    Keys: changed_counts (table -> (before, after)), mutated_rows
    (table -> list of differing row indices).
    """
    result: dict = {"changed_counts": {}, "mutated_rows": {}}
    for table in before:
        if table not in after:
            continue
        if before[table]["count"] != after[table]["count"]:
            result["changed_counts"][table] = (
                before[table]["count"], after[table]["count"]
            )
        if before[table]["rows"] != after[table]["rows"]:
            b_rows, a_rows = before[table]["rows"], after[table]["rows"]
            mutated = [
                i for i in range(max(len(b_rows), len(a_rows)))
                if i >= len(b_rows) or i >= len(a_rows) or b_rows[i] != a_rows[i]
            ]
            if mutated:
                result["mutated_rows"][table] = mutated
    return result


def assert_no_unexpected_mutation(before: dict, after: dict,
                                  allowed_tables: set[str] | None = None):
    """Assert nothing changed except (optionally) in whitelisted tables."""
    d = diff_snapshots(before, after)
    changed = set(d["changed_counts"]) | {
        t for t in d["mutated_rows"] if t not in (allowed_tables or set())
    }
    assert not changed, f"unexpected mutation in tables: {sorted(changed)}"
