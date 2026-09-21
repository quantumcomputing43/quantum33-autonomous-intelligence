import hashlib, json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

@dataclass
class MemoryRecord:
    record_id: str
    kind: str
    content: str
    source: str
    project: Optional[str]
    confidence: str
    created_at: str
    content_sha256: str

class MemoryStore:
    """Local structured memory. Memory is evidence, never command authority."""
    def __init__(self, root: Path):
        self.path = root / "memory.jsonl"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def add(self, record_id, kind, content, source, project=None, confidence="UNASSESSED"):
        record = MemoryRecord(record_id, kind, content, source, project, confidence,
                              datetime.now(timezone.utc).isoformat(),
                              hashlib.sha256(content.encode()).hexdigest())
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")
        return record

    def search(self, text, project=None):
        needle = text.lower()
        if not self.path.exists():
            return []
        out = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line: continue
            item = json.loads(line)
            if project is not None and item.get("project") != project: continue
            if needle in item.get("content", "").lower(): out.append(item)
        return out
