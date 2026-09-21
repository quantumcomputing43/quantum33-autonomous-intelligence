import math

from simulation.quantum_inspired import (
    basis_zero,
    hadamard,
    pauli_x,
    pauli_z,
    single_qubit_state,
)


def test_basis_zero_is_normalized():
    state = basis_zero(1)
    assert state.probabilities() == (1.0, 0.0)


def test_hadamard_creates_equal_probability_state():
    state = basis_zero(1).apply(hadamard())
    p0, p1 = state.probabilities()
    assert math.isclose(p0, 0.5, abs_tol=1e-12)
    assert math.isclose(p1, 0.5, abs_tol=1e-12)


def test_pauli_x_flips_basis_state():
    state = basis_zero(1).apply(pauli_x())
    assert state.probabilities() == (0.0, 1.0)


def test_pauli_z_preserves_zero_probability():
    state = basis_zero(1).apply(pauli_z())
    assert state.probabilities() == (1.0, 0.0)


def test_invalid_non_normalized_state_blocks():
    try:
        single_qubit_state((1.0, 1.0))
    except ValueError:
        pass
    else:
        raise AssertionError("Non-normalized state must be rejected")
