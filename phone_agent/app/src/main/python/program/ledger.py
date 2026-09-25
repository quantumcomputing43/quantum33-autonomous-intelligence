from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from program.storage import app_data_dir


class EvidenceLedger:
    """Append-only local evidence/event ledger."""

    def __init__(self, root: Path | None = None):
        self.root = Path(root) if root is not None else app_data_dir()
        self.path = self.root / "evidence_ledger.jsonl"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event, payload):
        item = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "payload": payload,
        }
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(item, ensure_ascii=False, sort_keys=True, default=str) + "\n")
        return item

    def record(self, event, payload):
        return self.append(event, payload)
