from dataclasses import dataclass, field


@dataclass
class DomElement:
    tag: str
    id: str = ""
    classes: list[str] = field(default_factory=list)
    attributes: dict[str, str] = field(default_factory=dict)
    text: str = ""
    position: tuple[int, int] | None = None
    parent_tag: str = ""
    parent_classes: list[str] = field(default_factory=list)
    unique: bool = True

    @classmethod
    def from_json(cls, raw: dict) -> "DomElement":
        return cls(
            tag=raw.get("tag", ""),
            id=raw.get("id", ""),
            classes=raw.get("classes", []),
            attributes=raw.get("attributes", {}),
            text=raw.get("text", ""),
            position=tuple(raw["position"]) if raw.get("position") else None,
            parent_tag=raw.get("parent_tag", ""),
            parent_classes=raw.get("parent_classes", []),
            unique=raw.get("unique", True),
        )


@dataclass
class FailureContext:
    selector: str
    selector_type: str = "css"
    page_url: str = ""
    action: str = ""
    error: str = ""

    @classmethod
    def from_json(cls, raw: dict) -> "FailureContext":
        return cls(
            selector=raw.get("selector", ""),
            selector_type=raw.get("selector_type", "css"),
            page_url=raw.get("page_url", ""),
            action=raw.get("action", ""),
            error=raw.get("error", ""),
        )


@dataclass
class Candidate:
    selector: str
    element_index: int
    score: float
    signals: dict[str, float] = field(default_factory=dict)


@dataclass
class HealingResult:
    original_selector: str
    healed_selector: str | None
    confidence: float
    mode: str
    rationale: str = ""
    candidates: list[Candidate] = field(default_factory=list)
