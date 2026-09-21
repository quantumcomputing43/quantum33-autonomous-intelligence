from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable, Sequence

import numpy as np


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
        matrix = np.asarray(gate, dtype=np.complex128)
        vector = np.asarray(self.amplitudes, dtype=np.complex128)
        if matrix.shape != (self.dimension, self.dimension):
            raise ValueError("Gate dimension does not match state dimension")
        out = matrix @ vector
        norm = float(np.linalg.norm(out))
        if not math.isfinite(norm) or norm <= 0:
            raise ValueError("Gate produced an invalid state")
        out = out / norm
        return QuantumInspiredState(tuple(complex(x) for x in out))

    def measure(self, rng: np.random.Generator | None = None) -> int:
        rng = rng or np.random.default_rng()
        return int(rng.choice(self.dimension, p=np.asarray(self.probabilities())))


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
