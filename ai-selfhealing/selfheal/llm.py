"""Optional agentic layer: OpenAI-compatible chat completions client.

Activates only when OPENAI_API_KEY is set (OPENAI_BASE_URL overrides the
endpoint, default https://api.openai.com/v1). Any transport or parsing error
degrades gracefully so callers can fall back to heuristic-only mode.
"""

import json
import os

import requests

DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = """You are a test-automation self-healing agent. Given a failed \
selector, a DOM snapshot, and ranked heuristic candidates, decide which candidate \
(or a better selector you construct from the DOM) targets the same semantic element \
as the original selector intended. Respond with ONLY a JSON object:
{"selector": "<css-or-xpath>", "confidence": <0..1>, "rationale": "<one sentence>"}"""

TOOL_CONTEXT_PROMPT = (
    "Request more DOM context by answering with "
    '{"need_context": true} if the candidates are all clearly wrong.'
)


class LlmAgent:
    def __init__(self, api_key: str | None = None, base_url: str | None = None,
                 model: str | None = None, timeout: float = 20.0):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.base_url = (base_url or os.environ.get("OPENAI_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
        self.model = model or os.environ.get("OPENAI_MODEL", DEFAULT_MODEL)
        self.timeout = timeout

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    def _chat(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        payload = {"model": self.model, "messages": messages}
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        resp = requests.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}",
                     "Content-Type": "application/json"},
            json=payload,
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()

    def heal(self, failure_prompt: str, candidates_summary: str, dom_summary: str) -> dict | None:
        if not self.available:
            return None
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT + "\n" + TOOL_CONTEXT_PROMPT},
            {"role": "user",
             "content": f"FAILURE:\n{failure_prompt}\n\nCANDIDATES:\n{candidates_summary}\n\nDOM:\n{dom_summary}"},
        ]
        tools = [{
            "type": "function",
            "function": {
                "name": "get_dom_context",
                "description": "Request a larger slice of the DOM snapshot when no candidate looks right",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        }]
        try:
            for _ in range(2):
                response = self._chat(messages, tools)
                choice = response["choices"][0]["message"]
                tool_calls = choice.get("tool_calls") or []
                if tool_calls and choice.get("finish_reason") == "tool_calls":
                    messages.append(choice)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_calls[0]["id"],
                        "content": dom_summary[:6000],
                    })
                    continue
                content = choice.get("content") or ""
                verdict = self._extract_json(content)
                if verdict and "selector" in verdict:
                    verdict["confidence"] = float(verdict.get("confidence", 0.0))
                    verdict["mode"] = "agent"
                    return verdict
                return None
        except (requests.RequestException, KeyError, ValueError, TypeError):
            return None
        return None

    @staticmethod
    def _extract_json(text: str) -> dict | None:
        text = text.strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.startswith("json"):
                text = text[4:]
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1:
            return None
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            return None
