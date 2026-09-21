import json
from datetime import datetime, timezone
from pathlib import Path

class EvidenceLedger:
    def __init__(self, root: Path):
        self.path = root / "evidence_ledger.jsonl"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def record(self, event, payload):
        item = {"timestamp": datetime.now(timezone.utc).isoformat(), "event": event, "payload": payload}
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n")
