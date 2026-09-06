"""Deterministic tool-use agent loop (offline): ReAct-style over local tools.

No LLM key needed: the planner is a rule-based policy (keyword -> tool),
every step is JSONL-traced, and the judge is exact-match on the final answer.
Swap `plan()` for a Claude/LangChain/LangGraph/DSPy planner without changing
tools, traces, or evals.
"""

import json
import time
from pathlib import Path

TRACE = Path(__file__).resolve().parent / "trace.jsonl"


def tool_health(args):
    import urllib.request

    with urllib.request.urlopen("http://127.0.0.1:8199/api/health", timeout=10) as res:
        return {"status": res.status, "body": json.loads(res.read())}


def tool_catalog(args):
    import urllib.request

    with urllib.request.urlopen("http://127.0.0.1:8199/api/products", timeout=10) as res:
        items = json.loads(res.read())
    q = (args.get("query") or "").lower()
    hits = [p for p in items if q in p["name"].lower()] if q else items
    return {"count": len(hits), "items": hits[:5]}


def tool_order_total(args):
    items = args.get("items", [])
    total = round(sum(i["price"] * i.get("quantity", 1) for i in items), 2)
    return {"total": total, "lines": len(items)}


TOOLS = {"get_health": tool_health, "search_catalog": tool_catalog, "order_total": tool_order_total}


def plan(task):
    t = task.lower()
    if "health" in t or "alive" in t or "up" in t:
        return [("get_health", {})]
    if "total" in t or "order" in t or "cart" in t:
        return [("search_catalog", {"query": ""}), ("order_total", {"items": []})]
    words = [w for w in t.split() if len(w) > 3]
    query = max(words, key=len) if words else ""
    return [("search_catalog", {"query": query})]


def run(task, trace_path=TRACE):
    steps = []
    for name, args in plan(task)[:5]:
        start = time.time()
        try:
            result = TOOLS[name](args)
            error = None
        except Exception as e:  # noqa: BLE001 - traced, never raised
            result, error = None, str(e)[:200]
        steps.append({"tool": name, "args": args, "result": result, "error": error,
                      "latency_ms": round((time.time() - start) * 1000, 1)})
    answer = summarize(task, steps)
    record = {"task": task, "steps": steps, "answer": answer}
    with open(trace_path, "a") as f:
        f.write(json.dumps(record) + "\n")
    return record


def summarize(task, steps):
    ok = [s for s in steps if not s["error"]]
    if not ok:
        return f"could not complete '{task}': " + "; ".join(s["error"] or "?" for s in steps)
    last = ok[-1]
    if last["tool"] == "get_health":
        return f"service is {last['result']['body'].get('status', '?')}"
    if last["tool"] == "search_catalog":
        return f"found {last['result']['count']} products"
    return f"done in {len(steps)} steps"


if __name__ == "__main__":
    import sys

    print(json.dumps(run(" ".join(sys.argv[1:]) or "is the service up?"), indent=2))
