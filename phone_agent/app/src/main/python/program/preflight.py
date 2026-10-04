from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class Risk:
    id: str
    severity: str
    condition: str
    detector: str
    mitigation: str


@dataclass
class PreflightReport:
    status: str
    project: str
    risks: list[Risk]
    scenarios: list[dict[str, Any]]
    required_evidence: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "project": self.project,
            "risks": [asdict(x) for x in self.risks],
            "scenarios": self.scenarios,
            "required_evidence": self.required_evidence,
        }


class PredictivePreflight:
    """Deterministic, tool-grounded risk scan executed before model actions."""

    def run(self, project: str, tree: Any, workflow_runs: Any | None = None) -> PreflightReport:
        text = repr(tree)
        risks: list[Risk] = []
        scenarios: list[dict[str, Any]] = []

        if "build.gradle" not in text and "settings.gradle" not in text:
            risks.append(Risk("PF-ANDROID-001","HIGH","Android build files not observed",
                              "repository tree scan","discover actual build root before editing"))
        if ".github/workflows" not in text:
            risks.append(Risk("PF-CI-001","HIGH","CI workflow directory not observed",
                              "repository tree scan","inspect CI before implementation"))
        if "pytest" in text:
            scenarios.append({"id":"S-PYTEST","failure":"Python tests fail",
                               "detector":"workflow job result","repair":"inspect failing test and root cause"})
        scenarios.extend([
            {"id":"S-AUTH","failure":"credential or permission failure",
             "detector":"GitHub/API response","repair":"verify permission/configuration; never guess credentials"},
            {"id":"S-IMPORT","failure":"import/path mismatch after repair",
             "detector":"test/import failure","repair":"reconcile actual package tree before changing imports"},
            {"id":"S-REGRESSION","failure":"repair breaks existing capability",
             "detector":"full test/build verification","repair":"rollback or redesign at architectural boundary"},
        ])
        if workflow_runs:
            runs = workflow_runs.get("workflow_runs", []) if isinstance(workflow_runs, dict) else []
            failed = [r for r in runs[:10] if r.get("conclusion") == "failure"]
            if failed:
                risks.append(Risk("PF-CI-HISTORY","MEDIUM","recent CI failures exist",
                                  "workflow history","inspect latest failure before repeating the strategy"))

        return PreflightReport(
            status="PREFLIGHT_READY" if not any(r.severity == "HIGH" for r in risks) else "PREFLIGHT_CAUTION",
            project=project,
            risks=risks,
            scenarios=scenarios,
            required_evidence=[
                "repository structure inspected",
                "planned changes tested",
                "verification result observed",
                "material failures have root-cause analysis",
            ],
        )
