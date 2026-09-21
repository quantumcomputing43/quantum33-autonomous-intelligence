"""Project snapshot metadata; read-only by default."""

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


@dataclass(frozen=True)
class Snapshot:
    project_id: str
    source: str
    captured_at: str
    manifest_sha256: str


class SnapshotManager:
    def __init__(self, root: str):
        self.root = Path(root)

    def manifest(self) -> str:
        entries = []
        if not self.root.exists():
            return ""
        for p in sorted(self.root.rglob("*")):
            if p.is_file():
                try:
                    data = p.read_bytes()
                except OSError:
                    continue
                entries.append((str(p.relative_to(self.root)), hashlib.sha256(data).hexdigest()))
        return json.dumps(entries, separators=(",", ":"), ensure_ascii=False)

    def capture(self, project_id: str, source: str) -> Snapshot:
        manifest = self.manifest()
        return Snapshot(
            project_id=project_id,
            source=source,
            captured_at=datetime.now(timezone.utc).isoformat(),
            manifest_sha256=hashlib.sha256(manifest.encode()).hexdigest(),
        )

    @staticmethod
    def to_dict(snapshot: Snapshot) -> dict:
        return asdict(snapshot)
