"""Selector parsing and multi-signal candidate scoring. Fully offline."""

import re
from difflib import SequenceMatcher

from .models import Candidate, DomElement, FailureContext

WEIGHTS = {
    "attribute": 0.35,
    "text": 0.25,
    "structural": 0.20,
    "position": 0.15,
    "uniqueness": 0.05,
}


def parse_selector(selector: str) -> dict:
    """Extract the intended target hints from a failed CSS/XPath selector."""
    info = {
        "tag": "",
        "id": "",
        "classes": [],
        "attributes": {},
        "text": "",
        "parent_tag": "",
        "parent_classes": [],
    }
    sel = selector.strip()
    if sel.startswith("//") or sel.startswith("("):
        tag_match = re.search(r"(?:^|/)([a-zA-Z][a-zA-Z0-9]*)", sel)
        if tag_match:
            info["tag"] = tag_match.group(1).lower()
        text_match = re.search(r"text\(\)\s*=\s*['\"]([^'\"]*)", sel) or re.search(
            r"contains\(text\(\),\s*['\"]([^'\"]*)", sel
        )
        if text_match:
            info["text"] = text_match.group(1)
        for attr_match in re.finditer(r"@([\w-]+)=['\"]([^'\"]*)['\"]", sel):
            info["attributes"][attr_match.group(1)] = attr_match.group(2)
        class_match = re.search(r"contains\(concat\(' ',\s*@class,\s*' '\),\s*' ([\w-]+) '\)", sel)
        if class_match:
            info["classes"].append(class_match.group(1))
        return info

    id_match = re.search(r"#([\w-]+)", sel)
    if id_match:
        info["id"] = id_match.group(1)
    info["classes"] = re.findall(r"\.([\w-]+)", sel)
    tag_match = re.match(r"^\s*([a-zA-Z][a-zA-Z0-9]*)", sel)
    if tag_match and not sel.startswith(("[", "*", ":")):
        info["tag"] = tag_match.group(1).lower()
    for attr_match in re.finditer(r"\[([\w-]+)(?:\*?=['\"]([^'\"]*)['\"])?\]", sel):
        name, value = attr_match.group(1), attr_match.group(2) or ""
        info["attributes"][name] = value
    text_match = re.search(r":contains\(['\"]([^'\"]*)['\"]\)", sel)
    if text_match:
        info["text"] = text_match.group(1)
    if " " in sel.strip() and not sel.startswith("//"):
        parent_part = sel.strip().rsplit(maxsplit=1)[0]
        parent_hints = parse_selector(parent_part)
        info["parent_tag"] = parent_hints["tag"]
        info["parent_classes"] = parent_hints["classes"]
    return info


def _ratio(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def attribute_similarity(hints: dict, element: DomElement) -> float:
    score = 0.0
    weight = 0.0
    if hints["id"]:
        weight += 0.5
        score += 0.5 * _ratio(hints["id"], element.id)
    hint_classes = set(hints["classes"])
    el_classes = set(element.classes)
    if hint_classes:
        weight += 0.3
        overlap = len(hint_classes & el_classes) / max(len(hint_classes | el_classes), 1)
        partial = (
            max((_ratio(h, e) for h in hint_classes for e in el_classes), default=0.0)
            * 0.5
        )
        score += 0.3 * min(overlap + partial, 1.0)
    hint_attrs = hints["attributes"]
    el_attrs = dict(element.attributes)
    if hint_attrs:
        weight += 0.2
        matched = 0.0
        for name, value in hint_attrs.items():
            if name in el_attrs:
                matched = max(matched, _ratio(value, el_attrs[name]) if value else 1.0)
                matched = max(matched, 0.5)
        score += 0.2 * matched
    if weight == 0.0:
        return 0.0
    return score / weight


def text_similarity(hints: dict, element: DomElement) -> float:
    hint_text = hints["text"].strip()
    el_text = element.text.strip()
    if not hint_text:
        return 0.5
    if not el_text:
        return 0.0
    ratio = _ratio(hint_text, el_text)
    if hint_text.lower() in el_text.lower():
        ratio = max(ratio, 0.9)
    return ratio


def structural_similarity(hints: dict, element: DomElement) -> float:
    score = 0.6 if not hints["tag"] else (1.0 if hints["tag"] == element.tag.lower() else 0.2)
    parent_component = 1.0
    if hints["parent_tag"]:
        tag_ok = hints["parent_tag"] == (element.parent_tag or "").lower()
        classes = set(hints["parent_classes"])
        el_classes = set(element.parent_classes or [])
        class_ok = not classes or bool(classes & el_classes)
        parent_component = 1.0 if (tag_ok and class_ok) else 0.2
    elif element.parent_tag:
        parent_component = 0.7
    return min(score + 0.3 * parent_component, 1.0)


def positional_similarity(failed_position: tuple | None, element: DomElement) -> float:
    if not failed_position or len(failed_position) < 2:
        return 0.5
    if not element.position or len(element.position) < 2:
        return 0.5
    dx = (failed_position[0] - element.position[0]) / 1000.0
    dy = (failed_position[1] - element.position[1]) / 1000.0
    distance = (dx**2 + dy**2) ** 0.5
    return max(0.0, 1.0 - min(distance, 1.0))


def uniqueness_factor(element: DomElement) -> float:
    return 1.0 if element.unique else 0.4


def build_selectors(element: DomElement) -> list[str]:
    selectors = []
    if element.id:
        selectors.append(f"#{element.id}")
    if element.classes:
        selectors.append("." + ".".join(sorted(element.classes)))
    if element.attributes.get("data-testid"):
        selectors.append(f"[data-testid='{element.attributes['data-testid']}']")
    if element.attributes.get("name"):
        selectors.append(f"[name='{element.attributes['name']}']")
    if element.text:
        escaped = element.text.strip()[:40].replace('"', "'")
        selectors.append(f"{element.tag}:has-text(\"{escaped}\")")
    base = element.tag
    if element.classes and element.id:
        selectors.append(f"{element.tag}#{element.id}.{'.'.join(sorted(element.classes))}")
    if base:
        selectors.append(base)
    seen, ordered = set(), []
    for s in selectors:
        if s not in seen:
            seen.add(s)
            ordered.append(s)
    return ordered


def rank_candidates(
    failure: FailureContext,
    elements: list[DomElement],
    top_n: int = 5,
    min_score: float = 0.25,
) -> list[Candidate]:
    hints = parse_selector(failure.selector)
    coord_match = re.search(r"\((-?\d+)\s*,\s*(-?\d+)\)", failure.error or "")
    pos = (
        (float(coord_match.group(1)), float(coord_match.group(2)))
        if coord_match
        else None
    )

    candidates: list[Candidate] = []
    for index, element in enumerate(elements):
        signals = {
            "attribute": attribute_similarity(hints, element),
            "text": text_similarity(hints, element),
            "structural": structural_similarity(hints, element),
            "position": positional_similarity(pos, element),
            "uniqueness": uniqueness_factor(element),
        }
        score = sum(WEIGHTS[k] * v for k, v in signals.items())
        if score < min_score:
            continue
        for selector in build_selectors(element)[:1]:
            candidates.append(
                Candidate(
                    selector=selector,
                    element_index=index,
                    score=round(min(score, 1.0), 4),
                    signals={k: round(v, 4) for k, v in signals.items()},
                )
            )
    candidates.sort(key=lambda c: c.score, reverse=True)
    return candidates[:top_n]
