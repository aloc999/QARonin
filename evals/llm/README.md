# LLM-eval Harness

Scores the self-healing locator engine (`ai-selfhealing`) on a fixed,
reviewed dataset (`dataset.jsonl`, 8 cases: id-rename, class-drift, stable...).

```bash
python evals/llm/eval.py          # or: make llm-eval
python -m pytest evals/llm/tests -q
```

Metrics: top-1 accuracy (gate >= 0.50), per-case latency, `eval-report.json`
(consumed by the Visual Report). Reuses the same `rank()` plumbing as the
production healer, so eval gains transfer directly. When `OPENAI_API_KEY`
is set, the agent path is exercised through the same cases (offline-first,
LLM optional).
