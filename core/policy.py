from enum import Enum
from dataclasses import dataclass

class IssueClass(str, Enum):
    MECHANICAL="MECHANICAL"
    PROVENANCE="PROVENANCE"
    SCIENTIFIC="SCIENTIFIC"
    AMBIGUOUS="AMBIGUOUS"

@dataclass(frozen=True)
class PolicyDecision:
    issue_class: IssueClass
    action: str
    reason: str

def classify_issue(issue_class: IssueClass, reason: str) -> PolicyDecision:
    action = {
        IssueClass.MECHANICAL: "ALLOW_MECHANICAL_REPAIR",
        IssueClass.PROVENANCE: "RECOVER_OR_BLOCK",
        IssueClass.SCIENTIFIC: "BLOCK",
        IssueClass.AMBIGUOUS: "BLOCK",
    }[issue_class]
    return PolicyDecision(issue_class, action, reason)
