"""Unit tests for MobileWait (no device needed): explicit waits retry until
the condition holds and raise TimeoutException when it never does."""

import os
import sys

import pytest
from selenium.common.exceptions import NoSuchElementException, TimeoutException

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.mobile_wait import MobileWait


class FakeElement:
    def is_displayed(self):
        return True


class FlakyDriver:
    """Fails the first two lookups, then resolves: proves retry, not sleep."""

    def __init__(self):
        self.calls = 0

    def find_element(self, by, value):
        self.calls += 1
        if self.calls < 3:
            raise NoSuchElementException("not yet")
        return FakeElement()


class NeverDriver:
    def find_element(self, by, value):
        raise NoSuchElementException("never")


def test_present_retries_then_resolves():
    wait = MobileWait(FlakyDriver(), timeout=5)
    assert isinstance(wait.present(("id", "x")), FakeElement)


def test_present_times_out_with_timeout_exception():
    wait = MobileWait(NeverDriver(), timeout=1)
    with pytest.raises(TimeoutException):
        wait.present(("id", "x"))
