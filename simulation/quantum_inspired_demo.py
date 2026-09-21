from __future__ import annotations

from .quantum_inspired import basis_zero, hadamard


def run_demo() -> dict[str, object]:
    state = basis_zero(1).apply(hadamard())
    return {
        "model": "classical quantum-inspired state-vector",
        "qubits": state.qubits,
        "dimension": state.dimension,
        "probabilities": state.probabilities(),
    }


if __name__ == "__main__":
    print(run_demo())
