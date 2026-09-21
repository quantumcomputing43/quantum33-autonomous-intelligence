from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class ReasoningBackend(Protocol):
    def answer(self, prompt: str, context: str = "") -> str:
        ...


@dataclass
class PromptBrain:
    """Prompt/context orchestration layer.

    A model backend can be attached later. Model output is analysis/evidence only;
    it never becomes command authority.
    """

    system_contract: str = (
        "You are the forensic reasoning layer. Preserve the scientific contract. "
        "Do not invent missing hypotheses, endpoints, thresholds, controls, or assumptions. "
        "If required information is missing, report BLOCKED."
    )

    def build_prompt(self, user_command: str, context: str = "") -> str:
        return (
            f"{self.system_contract}\n\n"
            f"USER COMMAND:\n{user_command}\n\n"
            f"CONTEXT:\n{context}"
        )
