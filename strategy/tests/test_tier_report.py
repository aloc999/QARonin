import os
import sys

import pytest

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
)

from tier_report import parse_budgets, build_report, main, parse_junit  # noqa: E402


@pytest.fixture
def testsuites_xml(tmp_path):
    content = """<?xml version="1.0" encoding="utf-8"?>
<testsuites name="playwright" tests="17" failures="0" time="20.9">
  <testsuite name="chromium/smoke" tests="3" failures="0" errors="0" skipped="0" time="4.1"/>
  <testsuite name="chromium/e2e" tests="1" failures="0" errors="0" skipped="0" time="6.3"/>
  <testsuite name="firefox/regression" tests="4" failures="1" errors="0" skipped="0" time="9.5"/>
</testsuites>
"""
    p = tmp_path / "ui.xml"
    p.write_text(content)
    return str(p)


@pytest.fixture
def bare_testsuite_xml(tmp_path):
    content = """<?xml version="1.0"?>
<testsuite name="api-python" tests="33" failures="0" errors="0" skipped="0" time="0.57"/>
"""
    p = tmp_path / "api.xml"
    p.write_text(content)
    return str(p)


class TestParseJunit:
    def test_nested_testsuites(self, testsuites_xml):
        report = parse_junit(testsuites_xml)
        assert len(report.suites) == 3
        assert report.total_tests == 8
        assert report.total_failures == 1
        assert abs(report.total_time - (4.1 + 6.3 + 9.5)) < 0.001

    def test_bare_testsuite_root(self, bare_testsuite_xml):
        report = parse_junit(bare_testsuite_xml)
        assert len(report.suites) == 1
        assert report.suites[0].name == "api-python"
        assert report.suites[0].tests == 33

    def test_missing_file_raises(self):
        with pytest.raises(OSError):
            parse_junit("/nonexistent/report.xml")

    def test_unexpected_root_raises(self, tmp_path):
        p = tmp_path / "bad.xml"
        p.write_text("<somethingelse/>")
        with pytest.raises(ValueError, match="unexpected root"):
            parse_junit(str(p))

    def test_zero_time_and_counts(self, tmp_path):
        p = tmp_path / "empty.xml"
        p.write_text('<testsuite name="x" tests="0" failures="0" errors="0" skipped="0" time="0"/>')
        report = parse_junit(str(p))
        assert report.total_tests == 0
        assert report.total_time == 0


class TestParseBudgets:
    def test_single_budget(self):
        assert parse_budgets(["ui=600"]) == {"ui": 600.0}

    def test_multiple_budgets(self):
        assert parse_budgets(["ui=600", "api=300"]) == {"ui": 600.0, "api": 300.0}

    def test_fractional_seconds(self):
        assert parse_budgets(["fast=0.5"]) == {"fast": 0.5}

    def test_missing_equals_rejected(self):
        with pytest.raises(ValueError, match="expected suite=seconds"):
            parse_budgets(["ui600"])

    def test_non_numeric_rejected(self):
        with pytest.raises(ValueError, match="invalid budget seconds"):
            parse_budgets(["ui=abc"])


class TestBuildReport:
    def test_report_contains_totals(self, testsuites_xml, bare_testsuite_xml):
        out = build_report([testsuites_xml, bare_testsuite_xml], {})
        assert "TOTAL" in out
        assert "41" in out
        assert "PASS" in out
        assert "FAIL" in out

    def test_over_budget_flagged(self, bare_testsuite_xml):
        out = build_report([bare_testsuite_xml], {"api": 0.1})
        assert "OVER BUDGET" in out
        assert "all declared budgets met" not in out

    def test_within_budget_flagged_clean(self, bare_testsuite_xml):
        out = build_report([bare_testsuite_xml], {"api": 300})
        assert "all declared budgets met" in out


class TestMain:
    def test_exit_zero_when_all_pass(self, tmp_path):
        p = tmp_path / "ok.xml"
        p.write_text('<testsuite name="ok" tests="2" failures="0" errors="0" skipped="0" time="1"/>')
        assert main([str(p), "--budget", "ok=10"]) == 0

    def test_exit_one_on_failure(self, tmp_path):
        p = tmp_path / "bad.xml"
        p.write_text('<testsuite name="bad" tests="2" failures="1" errors="0" skipped="0" time="1"/>')
        assert main([str(p)]) == 1

    def test_exit_one_on_over_budget(self, tmp_path):
        p = tmp_path / "slow.xml"
        p.write_text('<testsuite name="slow" tests="2" failures="0" errors="0" skipped="0" time="99"/>')
        assert main([str(p), "--budget", "slow=5"]) == 1
