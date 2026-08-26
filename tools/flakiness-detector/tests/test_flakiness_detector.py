import io
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import flakiness_detector as fd  # noqa: E402


def junit_xml(cases: list[tuple[str, str, str]]) -> str:
    """cases: list of (classname, name, outcome) where outcome is P/F/S."""
    parts = ['<testsuite name="suite" tests="%d">' % len(cases)]
    for classname, name, outcome in cases:
        if outcome == "P":
            parts.append(
                f'<testcase classname="{classname}" name="{name}" time="0.01"/>'
            )
        elif outcome == "F":
            parts.append(
                f'<testcase classname="{classname}" name="{name}" time="0.01">'
                "<failure message=\"boom\">x</failure></testcase>"
            )
        else:  # skipped
            parts.append(
                f'<testcase classname="{classname}" name="{name}" time="0.01">'
                "<skipped/></testcase>"
            )
    parts.append("</testsuite>")
    return "\n".join(parts)


@pytest.fixture
def run_file(tmp_path):
    def _write(cases, filename="run.xml"):
        p = tmp_path / filename
        p.write_text(junit_xml(cases), encoding="utf-8")
        return str(p)

    return _write


class TestParseJunit:
    def test_pass_fail_skip(self, run_file):
        outcomes = fd.parse_junit(
            run_file([("c", "t_pass", "P"), ("c", "t_fail", "F"), ("c", "t_skip", "S")])
        )
        assert outcomes == {"c::t_pass": True, "c::t_fail": False}

    def test_error_counts_as_failure(self, tmp_path):
        root = ET.Element("testsuite")
        case = ET.SubElement(root, "testcase", {"classname": "c", "name": "t"})
        ET.SubElement(case, "error", {"message": "err"})
        buf = io.BytesIO()
        ET.ElementTree(root).write(buf)
        p = tmp_path / "e.xml"
        p.write_bytes(buf.getvalue())
        assert fd.parse_junit(str(p)) == {"c::t": False}

    def test_missing_classname_uses_name_only(self, tmp_path):
        root = ET.Element("testsuite")
        ET.SubElement(root, "testcase", {"name": "bare"})
        buf = io.BytesIO()
        ET.ElementTree(root).write(buf)
        p = tmp_path / "b.xml"
        p.write_bytes(buf.getvalue())
        assert list(fd.parse_junit(str(p))) == ["bare"]


class TestClassify:
    def test_all_pass_stable(self):
        assert fd.classify([True, True, True]) == ("stable", None)

    def test_all_fail_broken(self):
        status, rate = fd.classify([False] * 4)
        assert status == "broken" and rate == 0.0

    def test_alternating_flaky_rate_one(self):
        status, rate = fd.classify([True, False, True, False])
        assert status == "flaky" and rate == 1.0

    def test_single_flip_rate(self):
        # one flip out of 4 transitions
        status, rate = fd.classify([True, True, True, True, False])
        assert status == "flaky" and rate == 0.25

    def test_regime_change_is_flaky(self):
        # mixed outcomes but no consecutive flips -> still flaky
        status, rate = fd.classify([False, False, True])
        assert status == "flaky"

    def test_min_runs_insufficient(self):
        assert fd.classify([True], min_runs=2) == ("insufficient-data", None)

    def test_min_runs_satisfied_boundary(self):
        assert fd.classify([True, False], min_runs=2)[0] == "flaky"


class TestCountFlips:
    def test_no_flips(self):
        assert fd.count_flips([True, True]) == 0
        assert fd.count_flips([False, False, False]) == 0

    def test_flips(self):
        assert fd.count_flips([True, False, True]) == 2
        assert fd.count_flips([True, True, False]) == 1


class TestLoadHistories:
    def test_merge_across_runs_ordered(self, run_file):
        f1 = run_file([("c", "a", "P")], "run-1.xml")
        f2 = run_file([("c", "a", "F"), ("c", "b", "P")], "run-2.xml")
        histories, labels = fd.load_histories([f1, f2])
        assert histories["c::a"] == [True, False]
        assert histories["c::b"] == [True]
        assert labels == [f1, f2]

    def test_late_added_test_has_partial_history(self, run_file):
        f1 = run_file([("c", "a", "P")], "run-1.xml")
        f2 = run_file([("c", "a", "P"), ("c", "new", "P")], "run-2.xml")
        histories, _ = fd.load_histories([f1, f2])
        assert histories["c::new"] == [True]


class TestBuildReport:
    def test_summary_counts_and_markdown(self):
        histories = {
            "s::ok": [True, True],
            "s::flip": [True, False, True],
            "s::dead": [False, False],
        }
        report, counts = fd.build_report(histories, min_runs=2)
        assert counts == {"stable": 1, "flaky": 1, "broken": 1,
                          "insufficient-data": 0}
        assert "# Flakiness report" in report
        assert "`s::flip` | flaky | 1.00" in report
        assert "- flaky: 1" in report


class TestEndToEnd:
    FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"

    @classmethod
    def RUNS(cls):
        return sorted((cls.FIXTURES / f"run-{i}.xml").as_posix() for i in range(1, 6))

    def test_cli_report_on_fixtures(self, capsys):
        rc = fd.main(self.RUNS())
        out = capsys.readouterr().out
        assert rc == 0
        assert "tests.ui::test_search_products" in out
        assert "| flaky | 1.00 |" in out
        assert "tests.ui::test_add_to_cart" in out
        assert "| flaky | 0.25 |" in out
        assert "tests.reports::test_admin_report" in out
        assert "- broken: 1" in out
        assert "- stable: 3" in out
        assert "- flaky: 2" in out

    def test_cli_glob_expansion(self, capsys):
        pattern = (self.FIXTURES / "run-*.xml").as_posix()
        rc = fd.main([pattern])
        out = capsys.readouterr().out
        assert rc == 0
        assert "Runs analyzed: 5" in out

    def test_cli_output_file(self, tmp_path, capsys):
        out_file = tmp_path / "report.md"
        rc = fd.main(self.RUNS() + ["-o", str(out_file)])
        assert rc == 0
        assert out_file.exists()
        assert "# Flakiness report" in out_file.read_text(encoding="utf-8")

    def test_cli_fail_on_flaky_exits_nonzero(self):
        with pytest.raises(SystemExit) as exc:
            fd.main(["--help"])
        # argparse help exits 0; real check below
        assert exc.value.code == 0
        rc = fd.main(self.RUNS() + ["--fail-on-flaky"])
        assert rc == 1

    def test_cli_min_runs_filters(self, capsys):
        # single run with --min-runs 3 -> everything is insufficient-data
        rc = fd.main(self.RUNS()[:1] + ["--min-runs", "3"])
        out = capsys.readouterr().out
        assert rc == 0
        assert "- stable: 0" in out
        assert "- flaky: 0" in out
        assert "- broken: 0" in out
        assert "insufficient-data: 5" in out

    def test_cli_broken_gate(self):
        runs_with_broken = self.RUNS()
        assert fd.main(runs_with_broken + ["--fail-on-broken"]) == 1

    def test_fixture_files_exist(self):
        for i in range(1, 6):
            assert (self.FIXTURES / f"run-{i}.xml").is_file()

    def test_two_tests_flip_in_fixtures(self):
        histories, _ = fd.load_histories(self.RUNS())
        statuses = [
            fd.classify(h)[0]
            for tid, h in sorted(histories.items())
            if h
        ]
        assert statuses.count("flaky") == 2
