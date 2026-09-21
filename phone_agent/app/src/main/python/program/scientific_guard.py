PROTECTED_TERMS = (
    "scientific question", "hypothesis", "mechanism", "endpoint",
    "threshold", "control", "null definition", "inclusion", "exclusion",
    "statistical criterion", "significance", "assumption"
)

def requires_scientific_decision(command: str) -> bool:
    c = command.lower()
    return any(term in c for term in PROTECTED_TERMS)

def guard_model_output(text: str) -> dict:
    """Model output can propose; it cannot authorize scientific changes."""
    return {
        "authority": "EVIDENCE_OR_PROPOSAL_ONLY",
        "scientific_changes_authorized": False,
        "text": text,
    }
