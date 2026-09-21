from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Command:
    text: str
    actor: str = "human"


class CommandRouter:
    """Routes only gateway-approved human commands to explicit operations."""

    def route(self, command: Command) -> str:
        if command.actor != "human":
            raise PermissionError("Only explicit human commands may be routed")
        text = command.text.strip()
        if not text:
            raise ValueError("Empty command")
        lowered = text.lower()
        if lowered.startswith("simulate "):
            return "simulation"
        if lowered.startswith("python "):
            return "python"
        if lowered.startswith("inspect "):
            return "inspection"
        if lowered.startswith("audit "):
            return "audit"
        return "reasoning"
