from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass
class CommandResult:
    accepted: bool
    status: str
    message: str

class AutonomousPhoneRuntime:
    """Phone-hosted entry point. Scientific policy is fail-closed."""

    def __init__(self):
        self.history = []

    def handle_human_command(self, command: str) -> str:
        command = command.strip()
        if not command:
            return "BLOCKED: empty command."
        result = CommandResult(
            accepted=True,
            status="RECEIVED",
            message="Command accepted by the human command gateway. Execution adapters are not enabled in this source-only build."
        )
        self.history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "command": command,
            "status": result.status,
        })
        return f"{result.status}: {result.message}"
