# DeepEval Harness (RAG + Conversational + Agentic)

Real LLM-as-judge evals with [DeepEval](https://github.com/confident-ai/deepeval):
Answer Relevancy, Faithfulness, Hallucination, Bias over a reviewed
`dataset.jsonl` (RAG pairs incl. a planted hallucination, injection
refusal, agentic tool traces).

```bash
pip install -r evals/deepeval/requirements.txt
python -m pytest evals/deepeval -q                       # offline suite (no key)
OPENAI_API_KEY=sk-... python -m pytest evals/deepeval -q  # + judged metrics
# or: make deepeval / AE_DEEPEVAL=1 nightly in CI
```

Without a key the judged tests SKIP; the offline suite (dataset integrity,
planted-hallucination grounding check, injection refusal, tool-trace scoring)
always runs in the gate. Thresholds: relevancy/faithfulness >= 0.7.
Complements `evals/llm` (self-heal locator scoring): different system under
test, same report consumer (`eval-report.json` shape documented in code).
