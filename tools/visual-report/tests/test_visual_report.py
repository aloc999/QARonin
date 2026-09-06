import subprocess
import sys
from pathlib import Path

GEN = Path(__file__).resolve().parent.parent / "generate.py"


def test_visual_report_renders_no_data(tmp_path):
    out = tmp_path / "report.html"
    r = subprocess.run(
        [sys.executable, str(GEN), "-o", str(out), "--title", "Test"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0
    text = out.read_text()
    assert "NO DATA" in text
    assert "Coverage" in text


def test_visual_report_with_junit(tmp_path):
    junit = tmp_path / "junit.xml"
    junit.write_text(
        '<testsuite tests="3" failures="1" errors="0" skipped="0" time="4.2">'
        '<testcase classname="a" name="t1"/><testcase classname="a" name="t2"/>'
        "</testsuite>"
    )
    out = tmp_path / "report.html"
    r = subprocess.run(
        [sys.executable, str(GEN), "--junit", str(junit), "-o", str(out)],
        capture_output=True, text=True,
    )
    assert r.returncode == 0
    text = out.read_text()
    assert "FAIL" in text
    assert "junit.xml" in text
