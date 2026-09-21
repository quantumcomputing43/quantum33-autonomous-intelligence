from dataclasses import dataclass, field
from datetime import datetime, timezone

@dataclass
class EvidenceRecord:
    event: str
    data: dict
    timestamp_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class EvidenceLedger:
    def __init__(self):
        self._records = []

    def append(self, event: str, data: dict) -> EvidenceRecord:
        record = EvidenceRecord(event, dict(data))
        self._records.append(record)
        return record

    def records(self):
        return tuple(self._records)
