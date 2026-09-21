# Two-Layer Architecture V1

## Purpose
The repository now has two deliberately separated layers.

### Layer A — Simulation
The simulation directory is the execution engine. It receives an explicit scientific contract and executes it. It records results and must stop when the contract is incomplete.

### Layer B — Autonomous Program
The program directory is the command-driven intelligence/orchestration layer. It is the interface through which the user can ask questions, inspect evidence, classify failures, request simulations, and run controlled Python analysis.

## Authority
The two layers share code, but neither GitHub nor another project can issue commands to the program. Only an explicit human-originated command accepted by the command gateway is executable authority.

## Isolation
- Project repositories are read-only by default.
- No automatic cross-project writes.
- No scientific contract mutation by either layer.
- Mechanical repair remains constrained to the existing repair policy.
- Every material action is written to the evidence ledger.

## Execution flow
Human Command -> Gateway -> Program -> Inspect/Reason -> Simulation or Python -> Verify -> Evidence Ledger -> Report

## Important capability statement
This is an autonomous forensic/audit architecture, not a claim of superintelligence. “Genius brain” is implemented as a design goal for broad reasoning/orchestration within explicit authority and scientific-integrity boundaries, not as an unsupported capability claim.
