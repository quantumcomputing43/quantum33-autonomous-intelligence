from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable, Sequence


@dataclass(frozen=True)
class QuantumInspiredState:
    """Small local state-vector model.

    This is a classical numerical simulation inspired by quantum state vectors.
    It is not a quantum computer and makes no claim of quantum advantage.
    """

    amplitudes: tuple[complex, ...]

    def __post_init__(self) -> None:
        if not self.amplitudes:
            raise ValueError("State must contain at least one amplitude")
        n = len(self.amplitudes)
        if n & (n - 1):
            raise ValueError("State dimension must be a power of two")
        norm = math.sqrt(sum(abs(a) ** 2 for a in self.amplitudes))
        if not math.isfinite(norm) or norm <= 0:
            raise ValueError("State must have finite non-zero norm")
        if not math.isclose(norm, 1.0, rel_tol=0.0, abs_tol=1e-12):
            raise ValueError("State must be normalized")

    @property
    def dimension(self) -> int:
        return len(self.amplitudes)

    @property
    def qubits(self) -> int:
        return int(math.log2(self.dimension))

    def probabilities(self) -> tuple[float, ...]:
        return tuple(float(abs(a) ** 2) for a in self.amplitudes)

    def apply(self, gate: Sequence[Sequence[complex]]) -> "QuantumInspiredState":
        matrix = tuple(tuple(complex(x) for x in row) for row in gate)
        if len(matrix) != self.dimension or any(len(row) != self.dimension for row in matrix):
            raise ValueError("Gate dimension does not match state dimension")
        out = tuple(
            sum(matrix[i][j] * self.amplitudes[j] for j in range(self.dimension))
            for i in range(self.dimension)
        )
        norm = math.sqrt(sum(abs(a) ** 2 for a in out))
        if not math.isfinite(norm) or norm <= 0:
            raise ValueError("Gate produced an invalid state")
        out = tuple(a / norm for a in out)
        return QuantumInspiredState(out)

    def measure(self, rng=None) -> int:
        import random
        rng = rng or random.Random()
        probabilities = self.probabilities()
        threshold = rng.random()
        cumulative = 0.0
        for index, probability in enumerate(probabilities):
            cumulative += probability
            if threshold <= cumulative:
                return index
        return self.dimension - 1


def basis_zero(qubits: int = 1) -> QuantumInspiredState:
    if qubits < 1:
        raise ValueError("qubits must be positive")
    amplitudes = [0j] * (2 ** qubits)
    amplitudes[0] = 1.0 + 0j
    return QuantumInspiredState(tuple(amplitudes))


def hadamard() -> tuple[tuple[complex, complex], tuple[complex, complex]]:
    s = 1.0 / math.sqrt(2.0)
    return ((s, s), (s, -s))


def pauli_x() -> tuple[tuple[complex, complex], tuple[complex, complex]]:
    return ((0j, 1.0 + 0j), (1.0 + 0j, 0j))


def pauli_z() -> tuple[tuple[complex, complex], tuple[complex, complex]]:
    return ((1.0 + 0j, 0j), (0j, -1.0 + 0j))


def single_qubit_state(amplitudes: Iterable[complex]) -> QuantumInspiredState:
    values = tuple(complex(x) for x in amplitudes)
    return QuantumInspiredState(values)
