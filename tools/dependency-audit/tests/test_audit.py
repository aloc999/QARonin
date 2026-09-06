import json
from pathlib import Path

from audit import PIN_RE, audit, parse_requirements


def test_pin_detection():
    assert PIN_RE.match("fastapi==0.141.1")
    assert PIN_RE.match("name==1.0; python_version>'3.8'")
    assert not PIN_RE.match("starlette<1.0.0")
    assert not PIN_RE.match("requests>=2")


def test_parse_requirements(tmp_path):
    f = tmp_path / "req.txt"
    f.write_text("# comment\nfastapi==0.141.1\nstarlette<1.0.0\n-r other.txt\n")
    reqs = parse_requirements(f)
    assert [r["name"] for r in reqs] == ["fastapi", "starlette"]
    assert reqs[0]["pinned"] and not reqs[1]["pinned"]


def test_audit_offline_flags_unpinned_but_no_vulns(tmp_path):
    f = tmp_path / "req.txt"
    f.write_text("a==1.0\nb>=2\n")
    rep = audit(f, online=False)
    assert rep["total"] == 2
    assert [r["name"] for r in rep["unpinned"]] == ["b"]
    assert rep["vulns"] == []


def test_real_requirements_are_mostly_pinned():
    root = Path(__file__).resolve().parent.parent.parent.parent
    rep = audit(root / "apps/demo-target/requirements.txt", online=False)
    assert rep["total"] >= 5
    names = [r["name"] for r in rep["unpinned"]]
    assert "starlette" in names  # documents the known range pin
