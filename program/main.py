from __future__ import annotations

import argparse

from .brain import PromptBrain
from .command_router import Command, CommandRouter
from .runtime import AutonomousProgram


def main() -> int:
    parser = argparse.ArgumentParser(description="Quantum33 Autonomous Intelligence")
    parser.add_argument("command", nargs="+", help="Explicit human command")
    args = parser.parse_args()

    command_text = " ".join(args.command)
    program = AutonomousProgram()
    program.handle(command_text, actor="human")

    route = CommandRouter().route(Command(command_text))
    prompt = PromptBrain().build_prompt(command_text)
    print(f"ROUTE={route}")
    print(prompt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
