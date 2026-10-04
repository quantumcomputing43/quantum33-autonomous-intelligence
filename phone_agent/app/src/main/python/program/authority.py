"""Explicit command authority and scientific-integrity boundaries."""
from dataclasses import dataclass
from enum import Enum

class Authority(str, Enum):
    HUMAN = "HUMAN"
    EXTERNAL = "EXTERNAL"

class Decision(str, Enum):
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    REQUIRE_HUMAN_AUTHORIZATION = "REQUIRE_HUMAN_AUTHORIZATION"

@dataclass(frozen=True)
class CommandEnvelope:
    text: str
    authority: Authority
    explicit_write_authorization: bool = False

def decide(envelope: CommandEnvelope) -> Decision:
    if envelope.authority is not Authority.HUMAN:
        return Decision.BLOCK
    lowered = envelope.text.lower()
    scientific_mutation = (
        "change hypothesis", "replace hypothesis", "change mechanism",
        "change endpoint", "change threshold", "change control",
        "change null definition", "change inclusion", "change exclusion",
        "change statistical criterion", "change scientific question",
        "invent hypothesis", "invent endpoint", "relax threshold",
        "remove control", "change null"
    )
    if any(term in lowered for term in scientific_mutation):
        return Decision.BLOCK
    write_terms = (
        "write", "commit", "push", "create pull request", "update repository",
        "delete file", "fix", "repair", "modify", "edit", "implement", "develop",
        "build the app", "change the app", "add feature", "run simulation",
        "simulation matrix", "dispatch workflow", "start simulation"
    )
    if any(x in lowered for x in write_terms):
        return (Decision.ALLOW if envelope.explicit_write_authorization
                else Decision.REQUIRE_HUMAN_AUTHORIZATION)
    return Decision.ALLOW
