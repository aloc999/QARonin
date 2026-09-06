import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from eval import load_dataset, evaluate, run  # noqa: E402


def test_dataset_loads():
    rows = load_dataset()
    assert len(rows) >= 8
    assert all("expected_selector" in r for r in rows)


def test_harness_reports_accuracy():
    report = run()
    assert report["total"] >= 8
    assert 0.0 <= report["accuracy"] <= 1.0
    assert report["accuracy"] >= 0.5
