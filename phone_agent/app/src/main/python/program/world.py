from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


TERMINAL_STATES = {
    "SUCCESS",
    "BLOCKED",
    "NO_VALID_PATH",
    "NEEDS_HUMAN_DECISION",
    "UNSAFE_OPERATION",
    "VERIFICATION_FAILED",
}


@dataclass
class WorldState:
    goal: str
    project: str | None = None
    phase: str = "DISCOVER"
    status: str = "RUNNING"
    cycle: int = 0
    plan: list[dict[str, Any]] = field(default_factory=list)
    scenarios: list[dict[str, Any]] = field(default_factory=list)
    observations: list[dict[str, Any]] = field(default_factory=list)
    failures: list[dict[str, Any]] = field(default_factory=list)
    repairs: list[dict[str, Any]] = field(default_factory=list)
    verification: list[dict[str, Any]] = field(default_factory=list)

    def terminal(self) -> bool:
        return self.status in TERMINAL_STATES

    def set_terminal(self, status: str) -> None:
        if status not in TERMINAL_STATES:
            raise ValueError("invalid terminal state")
        self.status = status


class EngineeringSupervisor:
    """State machine for predictive autonomous software engineering.

    The cycle guard is a safety brake, never a definition of intelligence.
    Completion is determined by verification or an explicit terminal state.
    """

    def __init__(self, max_cycles: int = 24):
        self.max_cycles = max_cycles

    def start(self, goal: str, project: str | None = None) -> WorldState:
        if not goal.strip():
            raise ValueError("empty goal")
        return WorldState(goal=goal.strip(), project=project)

    def record(self, state: WorldState, kind: str, payload: dict[str, Any]) -> None:
        getattr(state, kind).append(payload)

    def advance(self, state: WorldState) -> None:
        state.cycle += 1
        if state.cycle > self.max_cycles and not state.terminal():
            state.set_terminal("NO_VALID_PATH")
