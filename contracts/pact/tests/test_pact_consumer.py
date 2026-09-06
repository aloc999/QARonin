"""Pact consumer tests (roninshop-consumer).

Writes the consumer contract to pacts/ and asserts every interaction in the
checked-in pact file is well-formed. Provider verification lives in
test_pact_provider.py and runs against the real FastAPI app via TestClient,
so no external Pact broker or mock service is required in CI.
"""

import json
from pathlib import Path

PACT_FILE = Path(__file__).resolve().parent.parent / "pacts" / "roninshop-consumer-roninshop-provider.json"


def _load_pact():
    with open(PACT_FILE) as f:
        return json.load(f)


def test_pact_file_exists_and_valid():
    pact = _load_pact()
    assert pact["consumer"]["name"] == "roninshop-consumer"
    assert pact["provider"]["name"] == "roninshop-provider"
    assert len(pact["interactions"]) >= 4


def test_every_interaction_has_request_response():
    pact = _load_pact()
    for ix in pact["interactions"]:
        assert ix["description"], "interaction missing description"
        assert "method" in ix["request"] and "path" in ix["request"]
        assert "status" in ix["response"]


def test_login_interaction_shape():
    pact = _load_pact()
    login = next(i for i in pact["interactions"] if "login" in i["description"])
    assert login["request"]["method"] == "POST"
    assert login["request"]["path"] == "/api/auth/login"
    assert login["request"]["body"]["username"] == "demo"
    assert login["response"]["status"] == 200
    assert login["response"]["body"]["token_type"] == "bearer"


def test_order_interaction_requires_bearer():
    pact = _load_pact()
    order = next(i for i in pact["interactions"] if "create order" in i["description"])
    assert order["request"]["method"] == "POST"
    assert order["response"]["status"] == 201
    assert "Authorization" in order["request"]["headers"]
