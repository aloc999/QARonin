import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datadog_reporter import junit_metrics

OBS_DIR = Path(__file__).resolve().parent.parent


def _junit(tmp_path, tests=10, failures=2):
    f = tmp_path / "junit-x.xml"
    f.write_text(f'<testsuite tests="{tests}" failures="{failures}" errors="0"></testsuite>')
    return str(f)


def test_series_shape(tmp_path):
    series = junit_metrics(_junit(tmp_path))
    by_name = {s["metric"]: s["points"][0]["value"] for s in series}
    assert by_name == {"qaronin.tests.total": 10, "qaronin.tests.failed": 2, "qaronin.pass_rate": 0.8}


def test_tags_propagate(tmp_path):
    series = junit_metrics(_junit(tmp_path), tags=["env:ci"])
    assert all("env:ci" in s["tags"] for s in series)


def test_dry_run_without_key(tmp_path):
    r = subprocess.run(
        [sys.executable, "datadog_reporter.py", "--junit", _junit(tmp_path)],
        capture_output=True, text=True, cwd=str(OBS_DIR),
    )
    assert r.returncode == 0
    assert "DRY-RUN 3 series" in r.stdout


def test_main_dry_run_in_process(tmp_path, monkeypatch, capsys):
    import datadog_reporter

    monkeypatch.setattr(sys, "argv", ["datadog_reporter.py", "--junit", _junit(tmp_path)])
    monkeypatch.delenv("DD_API_KEY", raising=False)
    assert datadog_reporter.main() == 0
    assert "DRY-RUN 3 series" in capsys.readouterr().out


def test_post_ships_series(monkeypatch):
    import datadog_reporter

    seen = {}

    class FakeRes:
        status = 202

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    def fake_urlopen(req, timeout=20):
        seen["url"] = req.full_url
        seen["headers"] = {k.lower(): v for k, v in req.header_items()}
        return FakeRes()

    monkeypatch.setattr(datadog_reporter.urllib.request, "urlopen", fake_urlopen)
    assert datadog_reporter.post(datadog_reporter.SERIES_URL, "dummy-key", {"series": []}) == 202
    assert seen["url"] == datadog_reporter.SERIES_URL
    assert seen["headers"].get("dd-api-key") == "dummy-key"
