from .models import Candidate, DomElement, FailureContext
from .scoring import rank_candidates


def rank(
    failure: FailureContext, dom: list[DomElement], top_n: int = 5
) -> list[Candidate]:
    return rank_candidates(failure, dom, top_n=top_n)
