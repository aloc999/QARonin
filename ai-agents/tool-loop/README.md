# Tool-loop Agent (offline agentic demo)

A deterministic ReAct-style loop over local tools (`get_health`,
`search_catalog`, `order_total`) with JSONL traces. No API keys: the planner
is keyword rules; swap `plan()` for Claude/LangChain/LangGraph/DSPy without
changing tools, traces, or tests.

```bash
python ai-agents/tool-loop/agent.py "is the service up?"
python -m pytest ai-agents/tool-loop/tests -q   # needs live target on 8199 for 2 tests
# or: make agent-test
```
