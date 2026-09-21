"""Post-action verification hooks."""

from dataclasses import dataclass


@dataclass(frozen=True)
class VerificationResult:
    passed: bool
    checks: tuple[str, ...]
    failures: tuple[str, ...] = ()


class Verifier:
    def verify_text_artifact(self, before: str, after: str) -> VerificationResult:
        failures = []
        if not after:
            failures.append("EMPTY_ARTIFACT")
        if before == after:
            failures.append("NO_CHANGE")
        return VerificationResult(
            passed=not failures,
            checks=("non_empty", "change_detected"),
            failures=tuple(failures),
        )

    def verify_scientific_contract_unchanged(self, before: dict, after: dict) -> VerificationResult:
        protected = (
            "question", "hypothesis", "mechanism", "endpoint", "threshold",
            "controls", "inclusion", "exclusion", "null_definition",
            "statistical_criteria",
        )
        failures = [key for key in protected if before.get(key) != after.get(key)]
        return VerificationResult(
            passed=not failures,
            checks=("scientific_contract_unchanged",),
            failures=tuple(failures),
        )
