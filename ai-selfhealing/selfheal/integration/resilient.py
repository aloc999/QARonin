"""Resilient locator wrapper for Playwright (Python) tests.

Usage:
    from selfheal.integration.resilient import resilient

    button = resilient.locator(page, "#submit-order-btn")
    button.click()

On locator failure the engine heals the selector against a DOM snapshot
collected live from the page and retries with the top candidate; every
healing event is appended to selfheal-report.jsonl.

Requires playwright (pip install playwright) only at call time; importing
this module never requires it.
"""

import json
import time

from ..engine import rank_candidates
from ..models import DomElement, FailureContext
from ..report import log_healing_event


def collect_dom(page, limit: int = 400) -> list[DomElement]:
    raw = page.evaluate(
        """
        (limit) => Array.from(document.querySelectorAll('*')).slice(0, limit).map((el) => {
            const rect = el.getBoundingClientRect();
            return {
                tag: el.tagName.toLowerCase(),
                id: el.id || '',
                classes: Array.from(el.classList),
                attributes: Object.fromEntries(Array.from(el.attributes).map(a => [a.name, a.value])),
                text: (el.textContent || '').trim().slice(0, 120),
                position: [Math.round(rect.x), Math.round(rect.y)],
                parent_tag: el.parentElement ? el.parentElement.tagName.toLowerCase() : '',
                parent_classes: el.parentElement ? Array.from(el.parentElement.classList) : [],
                unique: el.id ? document.querySelectorAll('#' + CSS.escape(el.id)).length === 1 : true,
            };
        })
        """,
        limit,
    )
    return [DomElement.from_json(item) for item in raw]


class ResilientLocator:
    def __init__(self, page, selector: str, healer, on_heal=None):
        self._page = page
        self._selector = selector
        self._healer = healer
        self._on_heal = on_heal or log_healing_event

    @property
    def selector_used(self) -> str:
        return self._selector

    def _fail(self, failure: FailureContext):
        dom = collect_dom(self._page)
        result = self._healer.heal(failure, dom)
        self._on_heal(result)
        if result.healed_selector and result.confidence >= 0.5:
            self._selector = result.healed_selector

    def _wrap(self, method_name: str, *args, **kwargs):
        try:
            locator = self._page.locator(self._selector)
            getattr(locator, method_name)(*args, **kwargs)
            return locator
        except Exception as exc:
            failure = FailureContext(
                selector=self._selector,
                page_url=self._page.url,
                action=method_name,
                error=str(exc)[:500],
            )
            self._fail(failure)
            locator = self._page.locator(self._selector)
            getattr(locator, method_name)(*args, **kwargs)
            return locator

    def click(self, **kwargs):
        return self._wrap("click", **kwargs)

    def fill(self, value: str, **kwargs):
        return self._wrap("fill", value, **kwargs)

    def text_content(self, **kwargs):
        return self._page.locator(self._selector).text_content(**kwargs)


def resilient_locator(page, selector: str, healer=None):
    from ..healer import Healer

    return ResilientLocator(page, selector, healer or Healer())
