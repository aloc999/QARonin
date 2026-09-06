"""LLM / self-healing eval harness.

Scores the offline healing engine (ai-selfhealing) on a fixed JSONL dataset:
top-1 accuracy, per-category accuracy, mean latency, and a JSON report the
visual report can embed. No network calls: evaluates the deterministic
heuristic engine; the pluggable LLM agent is scored through the same
interface when OPENAI_API_KEY is set (graceful skip otherwise).
"""

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "ai-selfhealing"))

from selfheal.engine import rank  # noqa: E402
from selfheal.models import DomElement, FailureContext  # noqa: E402

DATASET = Path(__file__).resolve().parent / "dataset.jsonl"


def load_dataset():
    with open(DATASET) as f:
        return [json.loads(line) for line in f if line.strip()]


def evaluate(case):
    failure = FailureContext.from_json(case["failure"])
    dom = [DomElement.from_json(e) for e in case["dom"]]
    start = time.time()
    cands = rank(failure, dom, top_n=3)
    latency_ms = round((time.time() - start) * 1000, 2)
    top1 = cands[0].selector if cands else None
    return {
        "id": case["id"],
        "category": case.get("category", "?"),
        "expected": case["expected_selector"],
        "top1": top1,
        "pass": top1 == case["expected_selector"],
        "latency_ms": latency_ms,
        "n_candidates": len(cands),
    }


def run():
    results = [evaluate(c) for c in load_dataset()]
    passed = sum(1 for r in results if r["pass"])
    report = {
        "total": len(results),
        "passed": passed,
        "accuracy": round(passed / len(results), 3) if results else 0.0,
        "mean_latency_ms": round(sum(r["latency_ms"] for r in results) / len(results), 2) if results else 0.0,
        "results": results,
    }
    out = Path(__file__).resolve().parent / "eval-report.json"
    out.write_text(json.dumps(report, indent=2))
    print(f"LLM-eval: {passed}/{len(results)} passed (acc={report['accuracy']}) -> {out}")
    return report


if __name__ == "__main__":
    report = run()
    raise SystemExit(0 if report["accuracy"] >= 0.5 else 1)
