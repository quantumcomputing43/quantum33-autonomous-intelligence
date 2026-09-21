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


SCIENTIFIC_TERMS = (
    "hypothesis", "mechanism", "endpoint", "threshold", "control",
    "null definition", "inclusion", "exclusion", "statistical criterion",
    "scientific question",
)


def decide(envelope: CommandEnvelope) -> Decision:
    if envelope.authority is not Authority.HUMAN:
        return Decision.BLOCK

    lowered = envelope.text.lower()
    if any(term in lowered for term in SCIENTIFIC_TERMS):
        return Decision.BLOCK

    if any(x in lowered for x in ("write", "commit", "push", "create pull request", "update repository")):
        return (Decision.ALLOW if envelope.explicit_write_authorization
                else Decision.REQUIRE_HUMAN_AUTHORIZATION)

    return Decision.ALLOW
