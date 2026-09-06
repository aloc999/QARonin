import json
import subprocess
import sys
from pathlib import Path

COLLECT = Path(__file__).resolve().parent.parent / "collect.py"


def run_collect(tmp_path, *extra):
    out = tmp_path / "ev"
    r = subprocess.run(
        [sys.executable, str(COLLECT), "--stamp", "t1", "-o", str(out), *extra],
        capture_output=True, text=True, cwd=Path(__file__).resolve().parent.parent.parent.parent,
    )
    assert r.returncode == 0, r.stderr
    return json.loads((out / "t1" / "manifest.json").read_text())


def test_collect_from_repo_root():
    m = run_collect(Path("/tmp/qms-ev-t1"))
    kinds = {a["kind"] for a in m["artifacts"]}
    assert "junit" in kinds and "validation-plan" in kinds
    assert m["controls_index"]["junit"]


def test_gaps_recorded_not_fatal(tmp_path):
    m = run_collect(tmp_path)
    assert isinstance(m["gaps"], list)
