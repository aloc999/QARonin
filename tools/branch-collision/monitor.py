"""Branch-collision monitor: fail when two suites define the same test module.

We hit this exact bug (same-basename test_*.py collected under the wrong
suite). Scans test dirs for duplicate basenames and reports the collision
set. Exit 1 on collision (merge gate).
"""

import argparse
from collections import defaultdict
from pathlib import Path

DEFAULT_DIRS = [
    "apps/demo-target/tests", "frameworks/api-python/tests",
    "frameworks/selenium-py", "frameworks/appium-mobile/tests",
    "contracts/pact/tests", "observability/tests", "db-validation/tests",
    "ai-selfhealing/tests", "evals/llm/tests", "evals/deepeval",
    "frameworks/automationexercise/tests", "frameworks/bdd-python/features/steps",
    "tools/flakiness-detector/tests", "tools/visual-report/tests",
    "tools/vuln-aggregator/tests", "tools/dependency-audit/tests",
    "tools/qms-evidence/tests", "tools/site-monitor/tests",
    "tools/failure-triage/tests", "tools/quality-dashboard/tests",
    "tools/claims-diff/tests", "strategy/tests",
]


def find_collisions(root, dirs):
    seen = defaultdict(list)
    for d in dirs:
        for f in (Path(root) / d).glob("test_*.py"):
            seen[f.name].append(f"{d}/{f.name}")
    return {k: v for k, v in seen.items() if len(v) > 1}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    args = ap.parse_args()
    allow_path = Path(__file__).resolve().parent / "allowlist.txt"
    allowed = {l.strip() for l in allow_path.read_text().splitlines()
               if l.strip() and not l.startswith("#")} if allow_path.exists() else set()
    collisions = {k: v for k, v in find_collisions(args.root, DEFAULT_DIRS).items()
                  if k not in allowed}
    if collisions:
        print("branch-collision-monitor: NEW COLLISIONS (not in allowlist.txt)")
        for name, paths in sorted(collisions.items()):
            print(f"  {name}:")
            for p in paths:
                print(f"    - {p}")
        return 1
    print(f"branch-collision-monitor: no new collisions across {len(DEFAULT_DIRS)} dirs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
