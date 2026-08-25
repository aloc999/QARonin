"""JSONL healing-event report writer (selfheal-report.jsonl)."""

import json
import os
import threading
from datetime import datetime, timezone

DEFAULT_REPORT_PATH = "selfheal-report.jsonl"

_lock = threading.Lock()


def log_healing_event(result, report_path: str | None = None) -> str:
    path = report_path or os.environ.get("SELFHEAL_REPORT_PATH", DEFAULT_REPORT_PATH)
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "original_selector": result.original_selector,
        "healed_selector": result.healed_selector,
        "confidence": result.confidence,
        "mode": result.mode,
        "rationale": result.rationale,
        "candidates": [
            {"selector": c.selector, "score": c.score} for c in result.candidates
        ],
    }
    with _lock:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(event) + "\n")
    return path
