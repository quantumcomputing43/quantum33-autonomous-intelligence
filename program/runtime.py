from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.command_gateway import CommandGateway
from core.evidence_ledger import EvidenceLedger
from core.policy import IssueClass, classify_issue
from simulation.contracts import SimulationContract, SimulationEngine
from .python_executor import PythonExecutor


@dataclass
class ProgramResponse:
    status: str
    message: str
    payload: dict[str, Any]


class AutonomousProgram:
    """Human-command-driven orchestration layer."""

    def __init__(self) -> None:
        self.gateway = CommandGateway()
        self.ledger = EvidenceLedger()
        self.simulation = SimulationEngine()
        self.python = PythonExecutor()

    def handle(self, command: str, actor: str = "human") -> ProgramResponse:
        accepted = self.gateway.accept(command, actor=actor)
        self.ledger.append("COMMAND_ACCEPTED", {"actor": actor, "command": command})
        return ProgramResponse("ACCEPTED", "Human command accepted", {"command": accepted})

    def classify(self, description: str) -> IssueClass:
        return classify_issue(description)

    def run_simulation(self, contract: SimulationContract, runner) -> ProgramResponse:
        result = self.simulation.execute(contract, runner)
        self.ledger.append(
            "SIMULATION_RESULT",
            {"simulation_id": result.simulation_id, "status": result.status},
        )
        return ProgramResponse(result.status, "Simulation completed", {"result": result})
