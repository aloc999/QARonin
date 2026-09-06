import json
import subprocess
import sys
import time
from pathlib import Path

SERVER = Path(__file__).resolve().parent.parent / "server.py"


def _session(calls):
    """Speak MCP over stdio (newline-delimited JSON-RPC, FastMCP default)."""
    proc = subprocess.Popen(
        [sys.executable, str(SERVER)],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        text=True, bufsize=1,
    )

    def read_result(want_id, timeout_s=30):
        deadline = time.time() + timeout_s
        while time.time() < deadline:
            line = proc.stdout.readline()
            if not line:
                break
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue
            if msg.get("id") == want_id:
                return msg
        raise TimeoutError(f"no response for id {want_id}")

    def rpc(payload):
        proc.stdin.write(json.dumps(payload) + "\n")
        proc.stdin.flush()
        return read_result(payload["id"])

    def notify(payload):
        proc.stdin.write(json.dumps(payload) + "\n")
        proc.stdin.flush()

    init = rpc({"jsonrpc": "2.0", "id": 0, "method": "initialize",
                "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                           "clientInfo": {"name": "t", "version": "0"}}})
    assert init["result"]["serverInfo"]["name"] == "qaronin-qa"
    notify({"jsonrpc": "2.0", "method": "notifications/initialized"})
    out = [rpc(c) for c in calls]
    proc.stdin.close()
    proc.wait(timeout=60)
    return out


def test_tools_list():
    (res,) = _session([{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}])
    names = {t["name"] for t in res["result"]["tools"]}
    assert {"tier_report", "coverage_gate", "list_suites", "pact_status"} <= names


def test_list_suites_call():
    (res,) = _session([{"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                        "params": {"name": "list_suites", "arguments": {}}}])
    suites = json.loads(res["result"]["content"][0]["text"])
    assert "pact" in suites and "cypress" in suites


def test_coverage_gate_call_shape():
    (res,) = _session([{"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                        "params": {"name": "coverage_gate", "arguments": {"minimum": 0.5}}}])
    payload = json.loads(res["result"]["content"][0]["text"])
    assert isinstance(payload["ok"], bool)
    assert "line_rate" in payload or "error" in payload
