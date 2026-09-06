"""Stdlib-only observability helpers: structured JSON logs + run spans.

Keeps the demo-target dependency-free; OTel/Prometheus servers are optional
sidecars (see otel-collector-config.yaml, prometheus.yml). Test runs emit
JSONL spans the visual report can render.
"""

import json
import time
import uuid
from contextlib import contextmanager


def log_event(level, message, **fields):
    record = {"ts": time.time(), "level": level, "msg": message, **fields}
    print(json.dumps(record), flush=True)
    return record


@contextmanager
def span(name, **attrs):
    span_id = uuid.uuid4().hex[:16]
    start = time.time()
    log_event("info", f"span.start {name}", span_id=span_id, span=name, **attrs)
    try:
        yield span_id
    finally:
        dur_ms = round((time.time() - start) * 1000, 1)
        log_event("info", f"span.end {name}", span_id=span_id, span=name, duration_ms=dur_ms)
