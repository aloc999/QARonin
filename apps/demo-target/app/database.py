from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

_engine = None
_SessionLocal = None


def init_engine(db_url: str = "sqlite:///./roninshop.db"):
    global _engine, _SessionLocal
    _engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False, "timeout": 15},
    )

    @event.listens_for(_engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, _):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=15000")
        cursor.close()

    _SessionLocal = sessionmaker(bind=_engine, autoflush=False)
    return _engine


def get_session():
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()
