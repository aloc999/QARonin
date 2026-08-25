"""selfheal: agentic self-healing locator engine.

Deterministic offline heuristic mode plus optional LLM agent mode
(OpenAI-compatible chat completions). See README.md.
"""

from .models import DomElement, FailureContext, HealingResult
from .engine import rank_candidates
from .healer import Healer

__all__ = [
    "DomElement",
    "FailureContext",
    "HealingResult",
    "Healer",
    "rank_candidates",
]
