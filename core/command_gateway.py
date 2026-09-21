from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class Command:
    command_id: str
    actor: str
    operation: str
    payload: dict[str, Any]

class CommandGateway:
    def accept(self, command: Command) -> Command:
        if not command.command_id or not command.actor or not command.operation:
            raise ValueError("invalid explicit command")
        if command.actor != "human":
            raise PermissionError("only explicit human-originated commands are accepted")
        return command
