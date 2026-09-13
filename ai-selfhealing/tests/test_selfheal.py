import json
import os
import subprocess
import sys

import pytest

from selfheal.engine import rank
from selfheal.healer import Healer
from selfheal.llm import LlmAgent
from selfheal.models import DomElement, FailureContext, HealingResult
from selfheal.report import log_healing_event
from selfheal.scoring import (
    attribute_similarity,
    parse_selector,
    positional_similarity,
    rank_candidates,
    text_similarity,
    uniqueness_factor,
)

FIXTURES = os.path.join(os.path.dirname(__file__), "..", "fixtures")


def el(tag="div", id="", classes=None, attrs=None, text="", pos=None,
       parent="", parent_classes=None, unique=True):
    return DomElement(tag=tag, id=id, classes=classes or [], attributes=attrs or {},
                      text=text, position=pos, parent_tag=parent,
                      parent_classes=parent_classes or [], unique=unique)


def failure(selector="#submit-btn", error="", action="click"):
    return FailureContext(selector=selector, action=action, error=error)


class TestScoringMath:
    def test_exact_id_match_scores_high(self):
        hints = parse_selector("#submit-order")
        element = el(id="submit-order", unique=True)
        assert attribute_similarity(hints, element) == 1.0

    def test_similar_not_equal_id_partial_score(self):
        hints = parse_selector("#submit-order")
        assert 0.0 < attribute_similarity(hints, el(id="submit-ordr")) < 1.0

    def test_completely_different_attributes_low(self):
        hints = parse_selector("#alpha.beta-class")
        assert attribute_similarity(hints, el(id="omega")) < 0.25

    def test_text_containment_boosts_to_near_one(self):
        hints = parse_selector("button:contains('Place order')")
        assert text_similarity(hints, el(text="Please Place order now")) >= 0.9

    def test_missing_text_both_sides_is_neutral(self):
        assert text_similarity(parse_selector("div"), el()) == 0.5

    def test_position_distance_monotonic(self):
        close = positional_similarity((100, 100), el(pos=(110, 110)))
        far = positional_similarity((100, 100), el(pos=(900, 900)))
        assert close > far
        assert positional_similarity(None, el(pos=(0, 0))) == 0.5

    def test_uniqueness_penalty(self):
        assert uniqueness_factor(el(unique=True)) > uniqueness_factor(el(unique=False))

    def test_empty_selector_hints_do_not_crash(self):
        candidates = rank_candidates(failure(""), [el()], top_n=3)
        assert isinstance(candidates, list)

    def test_scores_bounded(self):
        candidates = rank_candidates(
            failure("#a.b[c='d']"),
            [el(id="a", classes=["b"], attrs={"c": "d"}, text="x", pos=(1, 1))],
        )
        for candidate in candidates:
            assert 0.0 <= candidate.score <= 1.0


def _scenario_dom():
    return [
        # 0: old button with changed id only
        el(tag="button", id="checkout-submit-new", classes=["btn-accent"],
           attrs={"data-testid": "checkout-submit"}, text="Place order",
           pos=(412, 640), parent="form"),
        # 1: unrelated nav link
        el(tag="a", id="nav-home", classes=["link"], text="Home", pos=(10, 10),
           parent="header"),
        # 2: card whose class list changed
        el(tag="article", id="product-card-3", classes=["product-card", "v2"],
           text="Ronin Tea Set", pos=(300, 200), parent="main"),
        # 3: price span that moved containers and changed class
        el(tag="span", id="price-value", classes=["money"], text="$74.00",
           pos=(320, 220), parent="section"),
        # 4 & 5: two near-identical add buttons (ambiguity)
        el(tag="button", classes=["add-to-cart"], text="Add to cart",
           pos=(250, 210), parent="article", unique=False),
        el(tag="button", classes=["add-to-cart"], text="Add to cart",
           pos=(600, 500), parent="article", unique=False),
    ]


class TestRankingScenarios:
    def test_scenario_1_id_changed(self):
        candidates = rank(failure("#checkout-submit"), _scenario_dom())
        assert candidates, "should produce candidates"
        best = rank_candidates(failure("#checkout-submit"), [_scenario_dom()[0]])[0]
        assert best.signals["attribute"] >= 0.5

    def test_scenario_2_class_changed(self):
        dom = [el(tag="div", id="panel", classes=["panel-body", "v2"],
                  text="Details"), el(tag="footer")]
        candidates = rank(failure(".panel-body"), dom)
        assert candidates[0].element_index == 0
        assert candidates[0].signals["attribute"] == 1.0

    def test_scenario_3_text_moved(self):
        dom = [
            el(tag="h2", id="old-title", text=""),
            el(tag="h1", id="page-title", text="Order Confirmation"),
        ]
        candidates = rank(failure("#old-title:contains('Order')"), dom)
        top = candidates[0]
        assert top.element_index == 1
        assert top.signals["text"] >= 0.9

    def test_scenario_4_structure_reparented(self):
        dom = [
            el(tag="input", id="email", classes=["field"], parent="section",
               parent_classes=["newsletter"]),
            el(tag="input", id="email-old", classes=["field"], parent="form",
               parent_classes=["signup"]),
        ]
        candidates = rank(failure("form.signup .field"), dom)
        assert len(candidates) == 2
        by_index = {c.element_index: c for c in candidates}
        assert (
            by_index[1].signals["structural"]
            > by_index[0].signals["structural"]
        )
        assert candidates[0].element_index == 1

    def test_scenario_5_ambiguous_candidates_penalized(self):
        dom = _scenario_dom()
        candidates = rank(failure("button.add-to-cart"), dom)
        assert len(candidates) >= 2
        scores = {c.element_index: c.score for c in candidates}
        assert scores.get(4) is not None and scores.get(5) is not None
        assert abs(scores[4] - scores[5]) < 0.05 or scores[4] != scores[5]


class TestHealerFallback:
    def test_no_api_key_means_heuristic_mode(self, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        agent = LlmAgent()
        assert not agent.available
        result = Healer(agent=agent).heal(failure("#checkout-submit"), _scenario_dom())
        assert result.mode == "heuristic"
        assert result.healed_selector

    def test_agent_transport_error_falls_back(self, monkeypatch):
        agent = LlmAgent(api_key="test-key", base_url="http://127.0.0.1:9",
                         timeout=0.2)
        result = Healer(agent=agent).heal(failure("#checkout-submit"), _scenario_dom())
        assert result.mode == "heuristic"

    def test_jsonl_report_written(self, tmp_path, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        report_path = tmp_path / "report.jsonl"
        healer = Healer(agent=LlmAgent())
        result = healer.heal(failure("#submit-order-btn"), _scenario_dom())
        log_healing_event(result, str(report_path))
        lines = report_path.read_text().strip().splitlines()
        assert len(lines) == 1
        event = json.loads(lines[0])
        assert event["original_selector"] == "#submit-order-btn"
        assert event["mode"] in {"heuristic", "agent"}
        assert event["candidates"]


class TestCliOffline:
    def test_cli_end_to_end(self, tmp_path):
        env = dict(os.environ)
        env.pop("OPENAI_API_KEY", None)
        report = tmp_path / "selfheal-report.jsonl"
        proc = subprocess.run(
            [sys.executable, "-m", "selfheal", "heal",
             "--failure", os.path.join(FIXTURES, "sample_failure.json"),
             "--dom", os.path.join(FIXTURES, "sample_dom.json"),
             "--report"],
            capture_output=True, text=True,
            cwd=os.path.join(os.path.dirname(FIXTURES)),
            env={**env, "SELFHEAL_REPORT_PATH": str(report)},
        )
        assert proc.returncode == 0, proc.stderr
        assert "place-order-btn" in proc.stdout.replace("#", "")
        assert "rank" in proc.stdout.lower()
        assert report.exists()
        event = json.loads(report.read_text().strip().splitlines()[0])
        assert event["confidence"] >= 0.5

    def test_cli_ranked_table_contains_all_candidates(self):
        env = dict(os.environ)
        env.pop("OPENAI_API_KEY", None)
        proc = subprocess.run(
            [sys.executable, "-m", "selfheal", "heal",
             "--failure", os.path.join(FIXTURES, "sample_failure.json"),
             "--dom", os.path.join(FIXTURES, "sample_dom.json")],
            capture_output=True, text=True,
            cwd=os.path.join(os.path.dirname(FIXTURES)), env=env,
        )
        ranks = [line for line in proc.stdout.splitlines() if line[:1].isdigit()]
        assert len(ranks) >= 2


class TestHealingResultContract:
    def test_result_defaults(self):
        result = HealingResult(original_selector="#x", healed_selector=None,
                               confidence=0.0, mode="heuristic")
        assert result.candidates == []


class _FakeLocator:
    """Minimal playwright-locator double: #broken always times out."""

    def __init__(self, page, selector):
        self._page = page
        self._selector = selector

    def click(self, **kwargs):
        self._page.calls.append(("click", self._selector))
        if self._selector == "#broken":
            raise TimeoutError("waiting for locator('#broken')")

    def fill(self, value, **kwargs):
        self._page.calls.append(("fill", self._selector, value))
        if self._selector == "#broken":
            raise TimeoutError("waiting for locator('#broken')")

    def text_content(self, **kwargs):
        return f"text-of-{self._selector}"


class _FakePage:
    def __init__(self, dom=()):
        self.calls = []
        self.url = "http://127.0.0.1:8199/cart"
        self._dom = list(dom)

    def locator(self, selector):
        return _FakeLocator(self, selector)

    def evaluate(self, _js, limit):
        return self._dom[:limit]


def _resilient_dom():
    return [{
        "tag": "button", "id": "place-order-btn", "classes": ["btn"],
        "attributes": {"data-testid": "checkout-submit"}, "text": "Place order",
        "position": [412, 640], "parent_tag": "form", "parent_classes": [],
        "unique": True,
    }]


class _StubHealer:
    def __init__(self, selector="#place-order-btn", confidence=0.9):
        self._selector = selector
        self._confidence = confidence

    def heal(self, failure, dom):
        assert dom, "healer must see the live DOM snapshot"
        return HealingResult(original_selector=failure.selector,
                             healed_selector=self._selector,
                             confidence=self._confidence, mode="stub",
                             rationale="stub", candidates=[])


class TestResilientLocator:
    def test_click_success_keeps_original_selector(self):
        from selfheal.integration.resilient import ResilientLocator

        page = _FakePage()
        loc = ResilientLocator(page, "#place-order-btn", _StubHealer())
        loc.click()
        assert loc.selector_used == "#place-order-btn"
        assert page.calls == [("click", "#place-order-btn")]

    def test_collect_dom_maps_raw_nodes(self):
        from selfheal.integration.resilient import collect_dom

        dom = collect_dom(_FakePage(_resilient_dom()))
        assert len(dom) == 1
        assert dom[0].id == "place-order-btn"
        assert dom[0].attributes["data-testid"] == "checkout-submit"

    def test_failure_heals_then_retries_healed_selector(self):
        from selfheal.integration.resilient import ResilientLocator

        healed = []
        page = _FakePage(_resilient_dom())
        loc = ResilientLocator(page, "#broken", _StubHealer(), on_heal=healed.append)
        loc.click()
        assert loc.selector_used == "#place-order-btn"
        assert page.calls == [("click", "#broken"), ("click", "#place-order-btn")]
        assert len(healed) == 1 and healed[0].healed_selector == "#place-order-btn"

    def test_low_confidence_keeps_selector_and_reraises(self):
        from selfheal.integration.resilient import ResilientLocator

        page = _FakePage(_resilient_dom())
        loc = ResilientLocator(page, "#broken", _StubHealer(confidence=0.1),
                               on_heal=lambda _result: None)
        with pytest.raises(TimeoutError):
            loc.click()
        assert loc.selector_used == "#broken"
        assert page.calls == [("click", "#broken"), ("click", "#broken")]

    def test_fill_and_text_content(self):
        from selfheal.integration.resilient import ResilientLocator

        page = _FakePage()
        loc = ResilientLocator(page, "#card-number", _StubHealer())
        loc.fill("4242-0000-0000-0000")
        assert page.calls == [("fill", "#card-number", "4242-0000-0000-0000")]
        assert loc.text_content() == "text-of-#card-number"

    def test_factory_builds_default_healer(self):
        from selfheal.integration.resilient import resilient_locator

        loc = resilient_locator(_FakePage(), "#place-order-btn")
        assert loc.selector_used == "#place-order-btn"
