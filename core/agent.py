from .command_gateway import Command, CommandGateway
from .evidence_ledger import EvidenceLedger

class AutonomousAuditAgent:
    def __init__(self):
        self.gateway = CommandGateway()
        self.ledger = EvidenceLedger()

    def execute(self, command: Command):
        accepted = self.gateway.accept(command)
        self.ledger.append("COMMAND_ACCEPTED", {"operation": accepted.operation})
        return {"status": "ACCEPTED", "operation": accepted.operation}
