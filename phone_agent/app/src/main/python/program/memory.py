from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

from program.storage import app_data_dir


@dataclass
class MemoryRecord:
    record_id: str
    content: str
    source: str
    project: str | None = None
    confidence: float | str = "UNASSESSED"
    created_at: str = ""
    content_sha256: str = ""


class LocalMemory:
    """Small bounded persistent memory; memory is evidence, never authority."""

    def __init__(self, root: Path | None = None, max_records: int = 256):
        self.root = Path(root) if root is not None else app_data_dir()
        self.path = self.root / "memory.jsonl"
        self.max_records = max(1, int(max_records))
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def remember(self, content: str, source: str = "unknown",
                 project: str | None = None, confidence: float | str = "UNASSESSED"):
        now = datetime.now(timezone.utc).isoformat()
        record = MemoryRecord(
            record_id=hashlib.sha256((now + content).encode("utf-8")).hexdigest()[:16],
            content=content,
            source=source,
            project=project,
            confidence=confidence,
            created_at=now,
            content_sha256=hashlib.sha256(content.encode("utf-8")).hexdigest(),
        )
        records = self._load()
        records.append(record)
        self._write(records[-self.max_records:])
        return record

    def recent(self, project: str | None = None):
        records = self._load()
        if project is not None:
            records = [r for r in records if r.project == project]
        return records[-self.max_records:]

    def search(self, text: str, project: str | None = None):
        needle = text.lower()
        return [r for r in self.recent(project) if needle in r.content.lower()]

    def _load(self):
        if not self.path.exists():
            return []
        out = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line:
                continue
            try:
                out.append(MemoryRecord(**json.loads(line)))
            except (TypeError, ValueError, json.JSONDecodeError):
                continue
        return out

    def _write(self, records):
        with self.path.open("w", encoding="utf-8") as f:
            for record in records:
                f.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")


MemoryStore = LocalMemory
