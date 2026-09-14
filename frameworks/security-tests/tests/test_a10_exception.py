"""A10-adjacent error handling: failure responses must never leak internals.

GET /api/flaky 10x covers both branches (200 ok, 503 transient): every body
must stay a clean JSON contract with no Python traceback. A 30%-failure
endpoint that ever rendered a stack trace would hand attackers file paths,
versions, and code structure — this pins the safe behavior.
"""

LEAK_MARKERS = ("Traceback (most recent call last)", '\nFile "', "File \"", ".py\", line")


def test_flaky_never_leaks_stack_trace(api):
    seen = set()
    for _ in range(10):
        res = api.get("/api/flaky")
        seen.add(res.status_code)
        assert res.status_code in (200, 503)
        assert res.headers["content-type"].startswith("application/json")
        for marker in LEAK_MARKERS:
            assert marker not in res.text
        body = res.json()
        if res.status_code == 503:
            assert set(body) == {"detail"}
        else:
            assert body["status"] == "ok"
    assert seen <= {200, 503}
