"""CLI: python -m selfheal heal --failure f.json --dom dom.json [--top N]"""

import argparse
import json
import os
import sys

from .healer import Healer
from .llm import LlmAgent
from .models import DomElement, FailureContext


def _load_failure(path: str) -> FailureContext:
    with open(path, encoding="utf-8") as fh:
        return FailureContext.from_json(json.load(fh))


def _load_dom(path: str) -> list[DomElement]:
    with open(path, encoding="utf-8") as fh:
        raw = json.load(fh)
    if isinstance(raw, dict):
        raw = raw.get("elements", [])
    return [DomElement.from_json(item) for item in raw]


def cmd_heal(args: argparse.Namespace) -> int:
    failure = _load_failure(args.failure)
    dom = _load_dom(args.dom)
    agent = LlmAgent()
    healer = Healer(agent=agent)
    result = healer.heal(failure, dom, top_n=args.top)

    print(f"original selector : {result.original_selector}")
    print(f"mode              : {result.mode}"
          + ("" if agent.available else " (no OPENAI_API_KEY; heuristic only)"))
    print(f"healed selector   : {result.healed_selector}")
    print(f"confidence        : {result.confidence}")
    print(f"rationale         : {result.rationale}")
    print()
    header = f"{'rank':<5}{'selector':<55}{'score':>7}"
    print(header)
    print("-" * len(header))
    for i, candidate in enumerate(result.candidates, 1):
        print(f"{i:<5}{candidate.selector:<55}{candidate.score:>7}")

    if args.report:
        from .report import log_healing_event
        path = log_healing_event(result)
        print(f"\nhealing event appended to {path}")
    return 0 if result.healed_selector else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="selfheal",
                                     description="Agentic self-healing locator engine")
    sub = parser.add_subparsers(dest="command", required=True)

    heal = sub.add_parser("heal", help="Heal a failed selector against a DOM snapshot")
    heal.add_argument("--failure", required=True, help="Path to failure-context JSON")
    heal.add_argument("--dom", required=True, help="Path to DOM-snapshot JSON")
    heal.add_argument("--top", type=int, default=5, help="Number of candidates to show")
    heal.add_argument("--report", action="store_true",
                      help=f"Append the event to the JSONL report "
                           f"(env SELFHEAL_REPORT_PATH, default {os.getcwd()}/selfheal-report.jsonl)")
    heal.set_defaults(func=cmd_heal)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
