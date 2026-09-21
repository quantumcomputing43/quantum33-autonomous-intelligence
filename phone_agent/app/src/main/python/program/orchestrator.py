from __future__ import annotations

from dataclasses import dataclass

from program.command_plan import classify_intent, Plan
from program.ledger import EvidenceLedger
from program.memory import LocalMemory
from program.provenance import normalize_evidence
from program.tool_router import ToolRouter, ToolSpec
from program.quantum_tool import run_demo


@dataclass
class AgentContext:
    command: str
    project: str | None
    evidence: list[dict]
    memory: list[dict]


class AgentOrchestrator:
    """Coordinates planning, evidence, memory and allowlisted local tools."""

    def __init__(self, ledger: EvidenceLedger | None = None,
                 memory: LocalMemory | None = None,
                 router: ToolRouter | None = None):
        self.ledger = ledger or EvidenceLedger()
        self.memory = memory or LocalMemory()
        self.router = router or ToolRouter()
        self.router.register(
            ToolSpec(
                "quantum_simulation",
                "Small classical quantum-inspired state-vector simulation",
                read_only=True,
            ),
            run_demo,
        )

    def plan(self, command: str) -> Plan:
        plan = classify_intent(command)
        self.ledger.append("PLAN_CREATED", {
            "intent": plan.intent,
            "tools": plan.tools,
            "read_only": plan.read_only,
        })
        return plan

    def context(self, command: str, project: str | None,
                evidence: list[dict]) -> AgentContext:
        normalized = normalize_evidence(evidence)
        memory = self.memory.recent(project=project)
        return AgentContext(
            command=command,
            project=project,
            evidence=[e.as_dict() for e in normalized],
            memory=[r.__dict__ for r in memory],
        )

    def run_quantum_demo(self, qubits: int = 1) -> dict:
        result = self.router.run("quantum_simulation", qubits=qubits)
        self.ledger.append("QUANTUM_SIMULATION", result)
        return result

    def record_command(self, command: str, project: str | None = None) -> None:
        self.ledger.append("COMMAND", {"command": command, "project": project})
        self.memory.remember(command, source="human_command", project=project, confidence=1.0)
