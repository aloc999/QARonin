from monitor import find_collisions, DEFAULT_DIRS
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent


def test_known_collisions_are_allowlisted():
    found = find_collisions(str(ROOT), DEFAULT_DIRS)
    new = set(found) - {l.strip() for l in open(ROOT / "tools/branch-collision/allowlist.txt")
                        if l.strip() and not l.startswith("#")}
    assert not new, f"new collisions: {new}"


def test_detector_spots_a_fresh_collision(tmp_path):
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    (tmp_path / "a" / "test_same.py").write_text("x = 1")
    (tmp_path / "b" / "test_same.py").write_text("x = 2")
    found = find_collisions(str(tmp_path), ["a", "b"])
    assert list(found) == ["test_same.py"]
