"""Healer orchestrator: heuristic ranking first, optional agent refinement."""

import json

from .llm import LlmAgent
from .models import Candidate, DomElement, FailureContext, HealingResult
from .scoring import rank_candidates


def _element_summary(element: DomElement, index: int) -> str:
    return json.dumps({
        "index": index,
        "tag": element.tag,
        "id": element.id,
        "classes": element.classes,
        "attributes": element.attributes,
        "text": element.text[:80],
    })


class Healer:
    def __init__(self, agent: LlmAgent | None = None):
        self.agent = agent or LlmAgent()

    def heal(self, failure: FailureContext, dom: list[DomElement],
             top_n: int = 5) -> HealingResult:
        candidates = rank_candidates(failure, dom, top_n=top_n)
        result = HealingResult(
            original_selector=failure.selector,
            healed_selector=candidates[0].selector if candidates else None,
            confidence=candidates[0].score if candidates else 0.0,
            mode="heuristic",
            rationale="Top-ranked deterministic candidate" if candidates else "No candidate scored above threshold",
            candidates=candidates,
        )
        if not self.agent.available or not candidates:
            return result

        candidates_summary = "\n".join(
            f"{i}. {c.selector} score={c.score} signals={c.signals}"
            for i, c in enumerate(candidates)
        )
        dom_summary = "\n".join(_element_summary(e, i) for i, e in enumerate(dom))
        failure_prompt = (
            f"selector={failure.selector!r} type={failure.selector_type} "
            f"url={failure.page_url} action={failure.action} error={failure.error}"
        )
        verdict = self.agent.heal(failure_prompt, candidates_summary, dom_summary)
        if verdict and verdict.get("confidence", 0.0) >= 0.5:
            result.mode = "agent"
            result.healed_selector = verdict["selector"]
            result.confidence = round(float(verdict["confidence"]), 4)
            result.rationale = verdict.get("rationale", "")
        elif verdict:
            result.rationale = (
                f"Agent rejected all candidates (confidence "
                f"{verdict.get('confidence', 0)}); keeping heuristic top pick. "
                + verdict.get("rationale", "")
            ).strip()
        return result
