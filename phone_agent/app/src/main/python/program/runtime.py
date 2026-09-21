from dataclasses import dataclass
from datetime import datetime, timezone

from program.authority import Authority, CommandEnvelope, Decision, decide


@dataclass
class CommandResult:
    accepted: bool
    status: str
    message: str


class AutonomousPhoneRuntime:
    """Phone-hosted entry point. Scientific policy is fail-closed."""

    def __init__(self):
        self.history = []

    def handle_human_command(
        self,
        command: str,
        repository: str = "",
        github_token: str = "",
        explicit_write_authorization: bool = False,
    ) -> str:
        command = command.strip()
        if not command:
            return "BLOCKED: empty command."

        envelope = CommandEnvelope(
            text=command,
            authority=Authority.HUMAN,
            explicit_write_authorization=explicit_write_authorization,
        )
        decision = decide(envelope)

        if decision is Decision.BLOCK:
            status = "BLOCKED"
            message = "Command violates an authority or scientific-integrity boundary."
            accepted = False
        elif decision is Decision.REQUIRE_HUMAN_AUTHORIZATION:
            status = "BLOCKED"
            message = "Explicit one-time write authorization is required."
            accepted = False
        else:
            status = "RECEIVED"
            message = (
                "Human command accepted. Runtime adapters remain execution-gated "
                "until each capability is independently verified."
            )
            accepted = True

        self.history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "command": command,
            "repository": repository,
            "github_credential_present": bool(github_token),
            "explicit_write_authorization": explicit_write_authorization,
            "decision": decision.value,
            "status": status,
        })
        return f"{status}: {message}"
