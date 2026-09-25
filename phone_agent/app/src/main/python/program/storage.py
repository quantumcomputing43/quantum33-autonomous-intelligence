from __future__ import annotations

import os
import tempfile
from pathlib import Path


def app_data_dir() -> Path:
    """Return a writable persistent directory on Android and desktop.

    Android/Chaquopy must not use Path.cwd() because the process working
    directory is not guaranteed to be writable. Prefer the app HOME, then
    the platform temp directory as a safe fallback.
    """
    candidates = []
    home = os.environ.get("HOME")
    if home:
        candidates.append(Path(home) / ".quantum33")
    candidates.append(Path(tempfile.gettempdir()) / ".quantum33")
    last_error = None
    for path in candidates:
        try:
            path.mkdir(parents=True, exist_ok=True)
            probe = path / ".write_probe"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink()
            return path
        except (OSError, PermissionError) as exc:
            last_error = exc
    raise OSError(f"No writable Quantum33 app data directory: {last_error}")
