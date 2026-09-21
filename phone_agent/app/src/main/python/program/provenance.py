from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass(frozen=True)
class Evidence:
    source: str
    source_type: str
    retrieved_at: str
    content_hash: str
    authority: str = "EVIDENCE_ONLY"

def make_evidence(source, source_type, content_hash):
    return Evidence(source, source_type, datetime.now(timezone.utc).isoformat(), content_hash)
