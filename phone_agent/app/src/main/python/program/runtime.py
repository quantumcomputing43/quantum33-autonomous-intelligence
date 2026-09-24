from dataclasses import dataclass
from datetime import datetime, timezone

from program.authority import Authority, CommandEnvelope, Decision, decide
from program.command_plan import classify_intent
from program.github_service import GitHubService
from program.brain import Brain, BrainContext
from program.model_provider import OpenAICompatibleBackend
from program.scientific_guard import guard_model_output
from program.orchestrator import AgentOrchestrator
from program.verification import verify_evidence


@dataclass
class CommandResult:
    accepted: bool
    status: str
    message: str


class AutonomousPhoneRuntime:
    """Phone-hosted orchestration entry point; fail-closed on authority boundaries."""

    def __init__(self):
        self.orchestrator = AgentOrchestrator()
        self.history = []

    def handle_human_command(
        self,
        command: str,
        repository: str = "",
        github_token: str = "",
        explicit_write_authorization: bool = False,
        model_endpoint: str = "",
        model_name: str = "",
        model_api_key: str = "",
    ) -> str:
        command = command.strip()
        if not command:
            return "BLOCKED: empty command."

        envelope = CommandEnvelope(
            text=command,
            authority=Authority.HUMAN,
            explicit_write_authorization=explicit_write_authorization,
        )
        decision = decide(envelope)
        self.orchestrator.record_command(command, repository or None)

        if decision is Decision.BLOCK:
            status = "BLOCKED"
            message = "Command attempts to change a protected scientific contract or violates authority."
            accepted = False
        elif decision is Decision.REQUIRE_HUMAN_AUTHORIZATION:
            status = "BLOCKED"
            message = "Explicit one-time write authorization is required."
            accepted = False
        else:
            status = "ACCEPTED"
            accepted = True
            plan = self.orchestrator.plan(command)
            evidence = []

            if "github" in plan.tools and repository and github_token:
                try:
                    service = GitHubService(github_token)
                    evidence.append({
                        "source": "github",
                        "kind": "repository",
                        "content": repr(service.repository(repository)),
                        "confidence": 0.9,
                    })
                    if any(x in command.lower() for x in ("workflow", "actions", "runs")):
                        evidence.append({
                            "source": "github",
                            "kind": "workflow_runs",
                            "content": repr(service.workflow_runs(repository)),
                            "confidence": 0.9,
                        })
                except Exception as exc:
                    evidence.append({
                        "source": "github",
                        "kind": "error",
                        "content": str(exc),
                        "confidence": 0.0,
                    })

            backend = None
            if model_endpoint and model_name and model_api_key:
                try:
                    backend = OpenAICompatibleBackend(model_endpoint, model_name, model_api_key)
                except Exception as exc:
                    evidence.append({
                        "source": "model",
                        "kind": "configuration_error",
                        "content": str(exc),
                        "confidence": 0.0,
                    })

            if "quantum_simulation" in plan.tools:
                try:
                    evidence.append({
                        "source": "local_quantum_simulator",
                        "kind": "simulation",
                        "content": repr(self.orchestrator.run_quantum_demo()),
                        "confidence": 1.0,
                    })
                except Exception as exc:
                    evidence.append({
                        "source": "local_quantum_simulator",
                        "kind": "error",
                        "content": str(exc),
                        "confidence": 0.0,
                    })

            ctx = self.orchestrator.context(command, repository or None, evidence)
            checkpoint = self.orchestrator.checkpoints.save("command", "EVIDENCE_COLLECTED", {"command": command, "evidence_count": len(evidence)})
            gate = verify_evidence(ctx.evidence)
            if gate["status"] != "PASS":
                return "BLOCKED: evidence verification failed."
            brain = Brain(backend)
            reasoning = brain.reason(BrainContext(
                command=ctx.command,
                evidence=ctx.evidence,
                memory=ctx.memory,
                project=ctx.project,
            ))
            if reasoning.get("status") == "MODEL_RESPONSE":
                safe = guard_model_output(reasoning.get("response", ""))
                message = safe["text"]
            else:
                message = (
                    "Command accepted. Local planning, provenance and evidence routing completed. "
                    "No model backend is configured."
                )

        self.history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "command": command,
            "repository": repository,
            "github_credential_present": bool(github_token),
            "model_configured": bool(model_endpoint and model_name and model_api_key),
            "explicit_write_authorization": explicit_write_authorization,
            "decision": decision.value,
            "status": status,
        })
        self.orchestrator.ledger.append("COMMAND_RESULT", {
            "command": command,
            "status": status,
            "decision": decision.value,
        })
        return f"{status}: {message}"
