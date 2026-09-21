from enum import Enum

class Decision(str, Enum):
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    REQUIRE_HUMAN_AUTHORIZATION = "REQUIRE_HUMAN_AUTHORIZATION"

class IssueClass(str, Enum):
    MECHANICAL = "MECHANICAL"
    PROVENANCE = "PROVENANCE"
    SCIENTIFIC = "SCIENTIFIC"
    AMBIGUOUS = "AMBIGUOUS"

def classify_text(text: str) -> IssueClass:
    lowered = text.lower()
    if any(k in lowered for k in ("threshold", "hypothesis", "endpoint", "null", "control", "mechanism")):
        return IssueClass.SCIENTIFIC
    if any(k in lowered for k in ("provenance", "source", "version", "historical", "artifact")):
        return IssueClass.PROVENANCE
    if any(k in lowered for k in ("syntax", "import", "path", "serialization", "logging", "checkpoint", "determinism")):
        return IssueClass.MECHANICAL
    return IssueClass.AMBIGUOUS

def authorize(issue_class: IssueClass) -> Decision:
    if issue_class is IssueClass.MECHANICAL:
        return Decision.ALLOW
    return Decision.BLOCK
