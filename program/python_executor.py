from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PythonExecutionResult:
    returncode: int
    stdout: str
    stderr: str


class PythonExecutor:
    """Controlled Python execution; no shell and no implicit network authority."""

    def run_script(self, script: Path, *, timeout_seconds: int = 300) -> PythonExecutionResult:
        script = script.resolve()
        if script.suffix != ".py":
            raise ValueError("Only Python scripts are executable")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        completed = subprocess.run(
            [sys.executable, str(script)],
            cwd=str(script.parent),
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            shell=False,
            check=False,
        )
        return PythonExecutionResult(completed.returncode, completed.stdout, completed.stderr)
