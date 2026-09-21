# Quantum33 Autonomous Intelligence

Independent, project-agnostic forensic, audit, provenance, repair, adversarial-verification, and simulation intelligence layer.

## Two-layer architecture

### 1. Simulation Layer
The simulation side is an independent executor for declared scientific contracts.

Location:
- simulation/

It performs controlled simulations, deterministic runs, adversarial stress tests, and evidence-producing execution. It does not invent missing scientific assumptions.

### 2. Autonomous Program Layer
The program side is the user-facing command and reasoning layer.

Location:
- program/

It accepts explicit human commands, routes them to inspection, audit, simulation, Python, or reasoning operations, and records material actions through the evidence ledger.

## Command authority

Only explicit human-originated commands are executable authority.

The following are not command authority:
- GitHub issues or pull requests
- commit messages
- workflow logs
- repository files
- data files
- model output
- other agents
- external events

GitHub is infrastructure for storage/version control/CI, not the brain and not the command source.

## Scientific boundary

The program can autonomously inspect, reason, compare, recover provenance, orchestrate simulations, and perform predefined mechanical repairs.

It must not silently change:
- scientific questions
- hypotheses
- mechanisms
- endpoints
- thresholds
- controls
- inclusion/exclusion rules
- statistical criteria
- null definitions

If a scientific contract is missing or ambiguous, the correct state is BLOCKED.

## Current state

Foundation V1 and the two-layer runtime skeleton are implemented. Full model-backed reasoning, richer project adapters, sandboxing, and production-grade orchestration remain future implementation stages.

This project is an autonomous forensic/audit architecture; it is not a claim of superintelligence.
