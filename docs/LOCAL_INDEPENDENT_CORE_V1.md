# Local Independent Core V1

## Purpose

The phone agent has a local core which can operate without GitHub credentials
and without an LLM backend for deterministic command acceptance, routing,
evidence bookkeeping, and controlled simulation modules.

GitHub is an optional external repository/tool provider, not the agent's brain
or command authority.

## Reasoning boundary

A local deterministic core is not the same thing as a self-aware or
superintelligent system. Higher-level open-ended reasoning requires an explicit
reasoning backend. The backend is treated as untrusted evidence/proposal
generation and cannot redefine scientific contracts or command authority.

## Quantum-inspired module

simulation/quantum_inspired.py implements a classical state-vector model:

- normalized complex amplitudes
- probability amplitudes and measurement
- Hadamard gate
- Pauli-X and Pauli-Z gates
- dimension constrained to powers of two

This is a mathematical simulation on a classical CPU. It is intentionally
described as quantum-inspired; it is not a quantum computer and does not imply
quantum advantage.

## Integrity rules

1. Scientific questions, hypotheses, endpoints, thresholds, controls and null
   definitions are never invented by the simulator.
2. Simulation contracts remain explicit and validated before execution.
3. Every new scientific simulation must declare its inputs, metrics,
   thresholds, controls and assumptions.
4. A simulation result is evidence, not automatic scientific truth.
5. GitHub access remains optional and separately authorized.
