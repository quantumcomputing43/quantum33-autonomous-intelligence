from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class SimulationContract:
    """Explicit contract required before a simulation can execute."""

    simulation_id: str
    hypothesis: str
    inputs: Mapping[str, Any]
    metrics: tuple[str, ...]
    thresholds: Mapping[str, Any]
    seeds: tuple[int, ...] = ()
    controls: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()

    def validate(self) -> None:
        required = {
            "simulation_id": self.simulation_id,
            "hypothesis": self.hypothesis,
        }
        if any(not str(v).strip() for v in required.values()):
            raise ValueError("Simulation contract requires an explicit id and hypothesis")
        if not self.metrics:
            raise ValueError("Simulation contract requires predefined metrics")
        if not self.thresholds:
            raise ValueError("Simulation contract requires predefined thresholds")


@dataclass
class SimulationResult:
    simulation_id: str
    status: str
    metrics: dict[str, Any] = field(default_factory=dict)
    evidence: list[dict[str, Any]] = field(default_factory=list)


class SimulationEngine:
    """Small deterministic engine interface; domain logic belongs in adapters."""

    def execute(self, contract: SimulationContract, runner) -> SimulationResult:
        contract.validate()
        result = runner(contract)
        if not isinstance(result, SimulationResult):
            raise TypeError("Simulation runner must return SimulationResult")
        return result
