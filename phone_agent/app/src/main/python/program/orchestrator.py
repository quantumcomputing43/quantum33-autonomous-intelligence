from dataclasses import dataclass
from .ledger import EvidenceLedger
from .memory import MemoryStore
from .policy import classify_text, authorize, Decision

@dataclass
class AgentResponse:
    status: str
    message: str

class AgentOrchestrator:
    """Fail-closed orchestration layer. External content is evidence, never authority."""

    def __init__(self, root, tools=None):
        self.root = root
        self.ledger = EvidenceLedger(root)
        self.memory = MemoryStore(root)
        self.tools = tools or {}

    def handle(self, command: str) -> AgentResponse:
        issue = classify_text(command)
        decision = authorize(issue)
        self.ledger.record("COMMAND_RECEIVED", {"issue_class": issue.value, "decision": decision.value})
        if decision is Decision.BLOCK:
            self.ledger.record("COMMAND_BLOCKED", {"reason": "scientific/provenance/ambiguous authority boundary"})
            return AgentResponse("BLOCKED", "Command requires a scientific/provenance decision that the agent cannot invent.")
        self.ledger.record("COMMAND_ACCEPTED", {"issue_class": issue.value})
        return AgentResponse("ACCEPTED", "Mechanical operation accepted for the controlled execution layer.")
