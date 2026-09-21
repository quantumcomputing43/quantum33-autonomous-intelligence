from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib

@dataclass
class EvidenceItem:
    kind: str
    source: str
    content: str
    authority: str = "EVIDENCE_ONLY"
    retrieved_at: str = ""
    content_hash: str = ""

    def finalize(self):
        self.retrieved_at = datetime.now(timezone.utc).isoformat()
        self.content_hash = hashlib.sha256(self.content.encode("utf-8")).hexdigest()
        return asdict(self)
