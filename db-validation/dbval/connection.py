"""Engine/session helpers. SQLite by default (the demo target's DB file),
Postgres or any other backend via DATABASE_URL."""

import os
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

_DEFAULT_SQLITE = (
    Path(__file__).resolve().parents[2] / "apps" / "demo-target" / "roninshop.db"
)


def database_url() -> str:
    url = os.environ.get("DATABASE_URL", "")
    if url:
        return url
    return f"sqlite:///{_DEFAULT_SQLITE}"


def create_db_engine(url: str | None = None):
    url = url or database_url()
    kwargs = {"future": True}
    if url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    return create_engine(url, **kwargs)


def make_session_factory(engine=None):
    engine = engine or create_db_engine()
    return sessionmaker(bind=engine, future=True)


def fetch_rows(session, sql: str, params: dict | None = None) -> list[tuple]:
    result = session.execute(text(sql), params or {})
    return [tuple(row) for row in result]
