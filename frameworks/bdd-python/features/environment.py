"""Behave environment: in-process TestClient (same pattern as api-python)."""

import os
import sys

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "apps", "demo-target")),
)

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.seed import seed  # noqa: E402


def before_all(context):
    seed(db_url="sqlite:///./test_bdd.db")
    context.client = TestClient(app)
    context.client.__enter__()
    context.tokens = {}
    context.last_response = None


def after_all(context):
    context.client.__exit__(None, None, None)
