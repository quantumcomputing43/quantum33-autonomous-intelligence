"""Deterministic local smoke tests for the phone agent core.

This module is intentionally dependency-free so it can run inside the phone's
Python runtime. It tests construction/integrity only; it does not validate any
scientific hypothesis.
"""

from program.authority import Authority, CommandEnvelope, Decision, decide
from program.memory import LocalMemory
from program.orchestrator import AgentOrchestrator
from program.quantum_inspired import basis_zero, hadamard


def run() -> dict:
    assert decide(CommandEnvelope("inspect repository", Authority.HUMAN)) is Decision.ALLOW
    assert decide(CommandEnvelope("change hypothesis", Authority.HUMAN)) is Decision.BLOCK
    assert decide(CommandEnvelope("commit this repair", Authority.HUMAN)) is Decision.REQUIRE_HUMAN_AUTHORIZATION

    memory = LocalMemory(max_records=2)
    memory.remember("a", "test")
    memory.remember("b", "test")
    memory.remember("c", "test")
    assert [x.content for x in memory.recent()] == ["b", "c"]

    agent = AgentOrchestrator()
    plan = agent.plan("run a quantum simulation")
    assert "quantum_simulation" in plan.tools
    quantum = agent.run_quantum_demo()
    assert quantum["status"] == "READY"
    assert len(quantum["probabilities"]) == 2
    assert abs(sum(quantum["probabilities"]) - 1.0) < 1e-12

    state = basis_zero(1).apply(hadamard())
    assert all(abs(p - 0.5) < 1e-12 for p in state.probabilities())

    return {"status": "PASS", "checks": 8}


if __name__ == "__main__":
    print(run())
