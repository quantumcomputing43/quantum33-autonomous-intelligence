from dataclasses import dataclass

MECHANICAL_CATEGORIES = frozenset({
    "syntax","import","path","serialization",
    "numerical_stability","determinism","checkpointing","logging"
})

@dataclass(frozen=True)
class RepairProposal:
    category: str
    description: str
    verification_required: bool = True

class RepairEngine:
    def propose(self, category: str, description: str) -> RepairProposal:
        if category not in MECHANICAL_CATEGORIES:
            raise PermissionError("scientific or unknown repair is blocked")
        return RepairProposal(category, description)
