from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib


@dataclass(frozen=True)
class Evidence:
    source: str
    source_type: str
    retrieved_at: str
    content_hash: str
    authority: str = "EVIDENCE_ONLY"

    def as_dict(self):
        return asdict(self)


def make_evidence(source, source_type, content_hash):
    return Evidence(
        source=source,
        source_type=source_type,
        retrieved_at=datetime.now(timezone.utc).isoformat(),
        content_hash=content_hash,
    )


def normalize_evidence(items):
    """Normalize untrusted evidence records without granting authority."""
    out = []
    for item in items or []:
        if isinstance(item, Evidence):
            out.append(item)
            continue
        source = str(item.get("source", "unknown"))
        source_type = str(item.get("kind", item.get("source_type", "unknown")))
        content = str(item.get("content", ""))
        content_hash = str(item.get("content_hash") or hashlib.sha256(content.encode("utf-8")).hexdigest())
        out.append(Evidence(
            source=source,
            source_type=source_type,
            retrieved_at=str(item.get("retrieved_at") or datetime.now(timezone.utc).isoformat()),
            content_hash=content_hash,
            authority="EVIDENCE_ONLY",
        ))
    return out
