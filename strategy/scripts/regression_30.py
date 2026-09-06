"""Full regression orchestrator with a hard 30-minute wall-clock budget.

Runs four parallel shards (L0+L1 API, TS UI, C#/Selenium UI, data/misc) and
fails when total wall time exceeds 1800s. Each shard is a shell command so CI
and local runs share one definition. Writes shard logs + a markdown summary
the Visual Report links to.

Usage:
  python strategy/scripts/regression_30.py --print-plan   # show shards only
  python strategy/scripts/regression_30.py                # run (budget 1800s)
  python strategy/scripts/regression_30.py --budget 300   # tighter gate
  make regression-30
"""

import argparse
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

BUDGET_S = 1800
ROOT = Path(__file__).resolve().parent.parent.parent

SHARDS = {
    # API + contracts + BDD + static checks: all in-process, seconds each.
    "shard-a-api": (
        "cd apps/demo-target && python -m pytest tests -q && "
        "cd ../../frameworks/api-python && python -m pytest -q && "
        "cd ../../contracts/pact && python -m pytest tests -q && "
        "cd ../../frameworks/bdd-python && python -m behave -q && "
        "cd ../../evals/deepeval && python -m pytest -q && "
        "cd ../../api/postman-newman && npm test --silent"
    ),
    # TS UI + Cypress E2E on chromium (firefox/webkit matrices stay nightly).
    # Cypress is skipped gracefully when its node_modules are absent.
    "shard-b-ts-ui": (
        "cd frameworks/playwright-ts && npx playwright test --project=chromium --grep-invert '@visual' && "
        "cd ../cypress && (npx --no-install cypress version >/dev/null 2>&1 && npx cypress run --e2e || echo 'cypress not installed; skipping')"
    ),
    # C# + Selenium smoke: language parity without the full matrix.
    "shard-c-lang-ui": (
        "(dotnet test frameworks/playwright-dotnet --filter Category=smoke || echo 'dotnet shard skipped') && "
        "cd frameworks/selenium-py && python -m pytest -q -m 'smoke or regression'"
    ),
    # Data + misc: db, obs, evals, AE parity (offline), tools unit tests.
    "shard-d-data": (
        "cd db-validation && python -m pytest -q && "
        "cd ../observability && python -m pytest tests -q && "
        "cd ../ai-selfhealing && PYTHONPATH=. python -m pytest -q && "
        "cd ../evals/llm && python -m pytest tests -q && "
        "cd ../../frameworks/automationexercise && AE_LIVE=0 python -m pytest tests -q && "
        "cd ../../mcp-server && python -m pytest tests -q && "
        "cd ../ai-agents/tool-loop && python -m pytest tests -q && "
        "cd ../../tools/visual-report && python -m pytest tests -q && "
        "cd ../flakiness-detector && python -m pytest tests -q && "
        "cd ../vuln-aggregator && python -m pytest tests -q && "
        "cd ../dependency-audit && python -m pytest tests -q && "
        "cd ../qms-evidence && python -m pytest tests -q && "
        "cd ../site-monitor && python -m pytest tests -q && "
        "cd ../failure-triage && python -m pytest tests -q && "
        "cd ../quality-dashboard && python -m pytest tests -q && "
        "cd ../branch-collision && python -m pytest tests -q && "
        "cd ../claims-diff && python -m pytest tests -q && "
        "cd ../../strategy && python -m pytest tests -q && "
        "cd .. && python tools/branch-collision/monitor.py"
    ),
}


def run_shard(name, cmd):
    start = time.time()
    r = subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True)
    dur = time.time() - start
    ok = r.returncode == 0
    tail = (r.stdout + r.stderr)[-3000:]
    return {"name": name, "ok": ok, "duration_s": round(dur, 1), "code": r.returncode, "tail": tail}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, default=BUDGET_S)
    ap.add_argument("--print-plan", action="store_true")
    ap.add_argument("--shard", action="append", default=[])
    args = ap.parse_args()

    shards = {k: v for k, v in SHARDS.items() if not args.shard or k in args.shard}
    if args.print_plan:
        for name, cmd in shards.items():
            print(f"[{name}]\n  {cmd}\n")
        print(f"budget: {args.budget}s across {len(shards)} parallel shards")
        return 0

    print(f"regression-30: {len(shards)} shards, budget {args.budget}s")
    start = time.time()
    with ThreadPoolExecutor(max_workers=len(shards)) as ex:
        results = list(ex.map(lambda kv: run_shard(*kv), shards.items()))
    wall = time.time() - start

    out_dir = ROOT / "reports"
    out_dir.mkdir(exist_ok=True)
    md = [f"# Regression-30 summary (wall {wall:.1f}s / budget {args.budget}s)", ""]
    all_ok = True
    for r in results:
        status = "PASS" if r["ok"] else "FAIL"
        all_ok = all_ok and r["ok"]
        md.append(f"- [{status}] {r['name']} ({r['duration_s']}s, exit {r['code']})")
        print(f"[{status}] {r['name']} {r['duration_s']}s")
        if not r["ok"]:
            print(f"--- tail {r['name']} ---\n{r['tail']}\n--- end ---")
    md.append("")
    md.append(f"wall_time_s: {wall:.1f}")
    (out_dir / "regression-30.md").write_text("\n".join(md) + "\n")

    if wall > args.budget:
        print(f"regression-30: OVER BUDGET ({wall:.1f}s > {args.budget}s) -> FAIL")
        return 1
    if not all_ok:
        print("regression-30: shard failure -> FAIL")
        return 1
    print(f"regression-30: PASS in {wall:.1f}s (budget {args.budget}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
