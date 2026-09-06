from dashboard import render, summarize


def test_summarize(tmp_path):
    f = tmp_path / "junit-a.xml"
    f.write_text('<testsuite tests="4" failures="1" errors="0"></testsuite>')
    assert summarize(str(f)) == {"run": "junit-a", "tests": 4, "failed": 1, "rate": 0.75}


def test_render_empty_and_full():
    assert "No history" in render([])
    html = render([{"run": "r1", "tests": 10, "failed": 0, "rate": 1.0}], "85%")
    assert "100%" in html and "85%" in html
