from __future__ import annotations

from program.quantum_inspired import basis_zero, hadamard


def run_demo(qubits: int = 1) -> dict:
    state = basis_zero(qubits)
    if qubits != 1:
        return {
            "status": "READY",
            "qubits": qubits,
            "probabilities": state.probabilities(),
            "note": "Local state-vector simulator; no quantum hardware claim.",
        }
    superposed = state.apply(hadamard())
    return {
        "status": "READY",
        "qubits": 1,
        "probabilities": superposed.probabilities(),
        "amplitudes": [str(a) for a in superposed.amplitudes],
        "note": "Classical numerical simulation of a quantum state vector.",
    }
