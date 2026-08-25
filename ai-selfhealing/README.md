# ai-selfhealing: Agentic Self-Healing Locator Engine

A Python package (`selfheal`) that repairs broken UI selectors at runtime.
Given a failed CSS/XPath selector and a DOM snapshot, it produces ranked
replacement candidates with per-signal scores and confidence values.

## Dual mode

| Mode | Trigger | Behavior |
|------|---------|----------|
| Heuristic (default) | always available, fully offline | Multi-signal deterministic scoring: attribute similarity (id/classes/attrs), fuzzy text similarity, structural match (tag + parent hints), positional proximity, uniqueness penalty. Produces ranked candidates + confidence. No network calls, no API key needed. |
| Agentic (optional) | `OPENAI_API_KEY` set (`OPENAI_BASE_URL` to point at any OpenAI-compatible endpoint) | The agent receives the failure context, top heuristic candidates and a DOM summary; it may issue one tool call (`get_dom_context`) to request more DOM context, then returns `{selector, confidence, rationale}` JSON. If the agent is unavailable, errors, or returns confidence < 0.5, the engine gracefully falls back to the heuristic top pick. |

Every healing decision can be explained: the result carries the full candidate
list with signal breakdowns plus (in agent mode) a natural-language rationale.

## Scoring model

```
score = 0.35 * attribute + 0.25 * text + 0.20 * structural
      + 0.15 * position + 0.05 * uniqueness
```

- attribute: id fuzzy ratio (0.5), class-set overlap + partial ratio (0.3), attribute match (0.2)
- text: SequenceMatcher ratio; containment boosts to >= 0.9; neutral 0.5 when the selector carried no text
- structural: tag equality plus parent tag/class hint agreement
- position: distance decay between failed-element coordinates and snapshot coordinates (neutral 0.5 if either missing)
- uniqueness: 1.0 for unique elements, 0.4 penalty for ambiguous matches

## CLI

```bash
cd ai-selfhealing
python -m selfheal heal --failure fixtures/sample_failure.json --dom fixtures/sample_dom.json
```

Prints mode, healed selector, confidence, rationale and a ranked candidate
table. Add `--report` to append the event to the JSONL report
(`SELFHEAL_REPORT_PATH`, default `selfheal-report.jsonl` in the CWD).

## Library usage

```python
from selfheal import Healer
from selfheal.llm import LlmAgent
from selfheal.models import DomElement, FailureContext

result = Healer(LlmAgent()).heal(
    FailureContext(selector="#submit-order-btn", action="click", error="TimeoutError"),
    [DomElement.from_json(e) for e in dom_json["elements"]],
)
print(result.healed_selector, result.confidence, result.mode)
```

## Playwright integration

`selfheal/integration/resilient.py` provides `resilient_locator(page, sel)`:
it attempts the original locator, and on failure collects a live DOM snapshot,
runs the healer, retries with the healed selector and appends the event to
`selfheal-report.jsonl`. Importing it never requires playwright; only calling.

`examples/healed-login.ts` is an annotated TypeScript port of the same pattern
for Node Playwright suites - example code only, deliberately not compiled or
executed by any build in this repo.

## Testing

```bash
python -m pytest        # scoring math edge cases, 5 ranking scenarios,
                        # offline CLI end-to-end, fallback w/o API key, JSONL report
```
