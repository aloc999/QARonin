import json

import pytest

from agent import TOOLS, plan, run


def test_plan_routes_keywords():
    assert plan("is the service up?")[0][0] == "get_health"
    assert [t for t, _ in plan("what is my order total?")] == ["search_catalog", "order_total"]
    assert plan("katana")[0] == ("search_catalog", {"query": "katana"})


def test_run_health_against_live_target(tmp_path):
    rec = run("is the service healthy?", trace_path=tmp_path / "t.jsonl")
    assert rec["steps"][0]["tool"] == "get_health"
    assert rec["steps"][0]["error"] is None
    assert "ok" in rec["answer"]
    assert (tmp_path / "t.jsonl").read_text().strip().startswith("{")


def test_run_catalog_search(tmp_path):
    rec = run("find katana gear", trace_path=tmp_path / "t.jsonl")
    assert rec["steps"][0]["result"]["count"] >= 1


def test_tool_order_total_pure():
    assert TOOLS["order_total"]({"items": [{"price": 10.0, "quantity": 2}]}) == {"total": 20.0, "lines": 1}


def test_all_tools_registered():
    assert set(TOOLS) == {"get_health", "search_catalog", "order_total"}
