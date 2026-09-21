"""Deterministic dependency-light integrity tests for the phone agent core.

These tests validate construction, routing, memory, evidence normalization,
authority boundaries and the local quantum-inspired simulator. They do not
validate any scientific hypothesis.
"""

from program.authority import Authority, CommandEnvelope, Decision, decide
from program.memory import LocalMemory
from program.orchestrator import AgentOrchestrator
from program.provenance import normalize_evidence
from program.quantum_inspired import basis_zero, hadamard
from program.runtime import AutonomousPhoneRuntime


def run() -> dict:
    checks = 0

    assert decide(CommandEnvelope("inspect repository", Authority.HUMAN)) is Decision.ALLOW
    checks += 1
    assert decide(CommandEnvelope("change hypothesis", Authority.HUMAN)) is Decision.BLOCK
    checks += 1
    assert decide(CommandEnvelope("commit this repair", Authority.HUMAN)) is Decision.REQUIRE_HUMAN_AUTHORIZATION
    checks += 1

    memory = LocalMemory(max_records=2)
    memory.remember("a", source="test")
    memory.remember("b", source="test")
    memory.remember("c", source="test")
    assert [x.content for x in memory.recent()] == ["b", "c"]
    checks += 1

    agent = AgentOrchestrator()
    plan = agent.plan("run a quantum simulation")
    assert "quantum_simulation" in plan.tools
    checks += 1

    quantum = agent.run_quantum_demo()
    assert quantum["status"] == "READY"
    assert len(quantum["probabilities"]) == 2
    assert abs(sum(quantum["probabilities"]) - 1.0) < 1e-12
    checks += 1

    ctx = agent.context(
        "inspect",
        None,
        [{"source": "test", "kind": "unit", "content": "evidence"}],
    )
    assert ctx.evidence and ctx.evidence[0]["authority"] == "EVIDENCE_ONLY"
    checks += 1

    normalized = normalize_evidence([{"source": "test", "kind": "unit", "content": "x"}])
    assert normalized[0].as_dict()["authority"] == "EVIDENCE_ONLY"
    checks += 1

    state = basis_zero(1).apply(hadamard())
    assert all(abs(p - 0.5) < 1e-12 for p in state.probabilities())
    checks += 1

    runtime = AutonomousPhoneRuntime()
    response = runtime.handle_human_command("Check your current runtime status. Do not modify anything.")
    assert response.startswith("ACCEPTED:")
    checks += 1

    return {"status": "PASS", "checks": checks}


if __name__ == "__main__":
    print(run())
