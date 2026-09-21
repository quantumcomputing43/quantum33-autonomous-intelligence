from dataclasses import dataclass
import subprocess
import sys

@dataclass
class ExecutionPolicy:
    timeout_seconds: int = 30
    allow_network: bool = False
    allow_write: bool = False

class ControlledPython:
    """Minimal execution boundary. Not a security sandbox."""

    def __init__(self, policy=None):
        self.policy = policy or ExecutionPolicy()

    def run(self, script: str):
        # Production sandboxing must be added before untrusted code is accepted.
        return subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True,
            text=True,
            timeout=self.policy.timeout_seconds,
            shell=False,
        )
