# QA MCP Server

`mcp-server/server.py` exposes QARonin quality tooling to coding agents over
MCP stdio (real `mcp` SDK, `FastMCP`): `tier_report`, `coverage_gate`,
`list_suites`, `pact_status`. All tools are read-only except `pact_status`
(which runs pytest in-process).

```bash
pip install -r mcp-server/requirements.txt
python mcp-server/server.py                 # stdio server
python -m pytest mcp-server/tests -q        # protocol tests (real handshake)
# or: make mcp-test
```

`.mcp.json` registers the server with MCP-aware clients. CI job `mcp`
runs the protocol tests (no network).
