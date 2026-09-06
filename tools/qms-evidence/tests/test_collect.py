import json
import subprocess
import sys
from pathlib import Path

COLLECT = Path(__file__).resolve().parent.parent / "collect.py"


def _fixture_tree(root: Path):
    (root / "svc").mkdir(parents=True, exist_ok=True)
    (root / "svc" / "junit.xml").write_text(
        '<testsuite tests="2" failures="0" errors="0"></testsuite>'
    )
    (root / "coverage.xml").write_text('<coverage line-rate="0.9"></coverage>')
    (root / "docs" / "QMS").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "QMS" / "VALIDATION-PLAN.md").write_text("# plan")


def run_collect(cwd, outdir, stamp="t1"):
    r = subprocess.run(
        [sys.executable, str(COLLECT), "--stamp", stamp, "-o", str(outdir)],
        capture_output=True, text=True, cwd=str(cwd),
    )
    assert r.returncode == 0, r.stderr
    return json.loads((outdir / stamp / "manifest.json").read_text())


def test_collect_bundles_kinds_and_controls(tmp_path):
    _fixture_tree(tmp_path)
    m = run_collect(tmp_path, tmp_path / "ev")
    kinds = {a["kind"] for a in m["artifacts"]}
    assert {"junit", "coverage", "validation-plan"} <= kinds
    assert m["controls_index"]["junit"]
    junit = next(a for a in m["artifacts"] if a["kind"] == "junit")
    assert junit["summary"] == {"tests": 2, "failures": 0, "errors": 0}


def test_gaps_recorded_not_fatal(tmp_path):
    m = run_collect(tmp_path, tmp_path / "ev")
    assert "visual-report" in m["gaps"] or "vuln-summary" in m["gaps"]
