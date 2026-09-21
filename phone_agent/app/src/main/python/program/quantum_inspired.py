from __future__ import annotations

from dataclasses import dataclass
import math
import random


@dataclass(frozen=True)
class QuantumInspiredState:
    """Classical state-vector simulator for small quantum-inspired calculations."""

    amplitudes: tuple[complex, ...]

    def __post_init__(self):
        n = len(self.amplitudes)
        if n < 2 or n & (n - 1):
            raise ValueError("state dimension must be a power of two and >= 2")
        norm = math.sqrt(sum(abs(a) ** 2 for a in self.amplitudes))
        if not math.isfinite(norm) or norm <= 0:
            raise ValueError("state norm must be finite and non-zero")
        if not math.isclose(norm, 1.0, rel_tol=0.0, abs_tol=1e-12):
            raise ValueError("state must be normalized")

    @property
    def dimension(self):
        return len(self.amplitudes)

    @property
    def qubits(self):
        return int(math.log2(self.dimension))

    def probabilities(self):
        return tuple(abs(a) ** 2 for a in self.amplitudes)

    def apply(self, gate):
        matrix = tuple(tuple(complex(x) for x in row) for row in gate)
        if len(matrix) != self.dimension or any(len(r) != self.dimension for r in matrix):
            raise ValueError("gate dimension does not match state")
        out = tuple(
            sum(matrix[i][j] * self.amplitudes[j] for j in range(self.dimension))
            for i in range(self.dimension)
        )
        norm = math.sqrt(sum(abs(a) ** 2 for a in out))
        if not math.isfinite(norm) or norm <= 0:
            raise ValueError("gate produced invalid state")
        return QuantumInspiredState(tuple(a / norm for a in out))

    def measure(self, rng=None):
        rng = rng or random.Random()
        threshold = rng.random()
        cumulative = 0.0
        for i, p in enumerate(self.probabilities()):
            cumulative += p
            if threshold <= cumulative:
                return i
        return self.dimension - 1


def basis_zero(qubits=1):
    if qubits < 1:
        raise ValueError("qubits must be positive")
    values = [0j] * (2 ** qubits)
    values[0] = 1.0 + 0j
    return QuantumInspiredState(tuple(values))


def hadamard():
    s = 1.0 / math.sqrt(2.0)
    return ((s, s), (s, -s))


def pauli_x():
    return ((0j, 1.0 + 0j), (1.0 + 0j, 0j))


def pauli_z():
    return ((1.0 + 0j, 0j), (0j, -1.0 + 0j))
