import time

import pytest


def retry_until_success(fn, max_attempts=10, initial_delay=0.05, backoff_factor=1.6):
    """
    Hand-rolled tenacity-style retry decorator replacement: calls fn until it
    returns a truthy value or attempts are exhausted. Exponential backoff.
    Returns (result, attempts_used).
    """
    delay = initial_delay
    last_exc = None
    for attempt in range(1, max_attempts + 1):
        try:
            result = fn()
            if result:
                return result, attempt
        except Exception as exc:
            last_exc = exc
        time.sleep(delay)
        delay *= backoff_factor
    raise AssertionError(
        f"retry_until_success exhausted {max_attempts} attempts"
        + (f"; last error: {last_exc}" if last_exc else "")
    )


@pytest.mark.regression
class TestFlakyEndpoint:
    def test_flaky_eventually_succeeds(self, api):
        result, attempts = retry_until_success(lambda: api.get("/api/flaky").status_code == 200)
        assert result is True
        assert attempts >= 1

    def test_flaky_never_returns_other_client_errors(self, api):
        for _ in range(20):
            res = api.get("/api/flaky")
            assert res.status_code in (200, 503)

    def test_retry_helper_gives_up_after_max_attempts(self):
        with pytest.raises(AssertionError, match="exhausted"):
            retry_until_success(lambda: False, max_attempts=3, initial_delay=0.001)
