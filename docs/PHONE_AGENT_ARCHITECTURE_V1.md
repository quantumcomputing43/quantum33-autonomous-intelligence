# Phone Agent Architecture V1

## Goal

The Autonomous Program becomes a standalone Android application on the user's phone. GitHub is infrastructure only: repository storage, version control, and API surface.

## Authority boundary

Only explicit human commands entered through the app are command authority.

The app MUST NOT treat GitHub issues, PR comments, commit messages, workflow logs, repository files, fetched web pages, model output, simulation output, or other agents as commands.

## Layers

1. Android UI / secure command entry
2. Command Gateway
3. Python Agent Core
4. Memory + provenance store
5. Reasoning backend interface
6. Tool router: web/knowledge, Python, GitHub, simulation
7. Evidence ledger
8. Policy / scientific-integrity guard
9. Repository adapters

## Repository control

The phone agent may read and modify repositories through an explicitly configured GitHub credential. Default mode is read-only. Write operations require explicit human authorization and are logged.

## Scientific integrity

The agent can inspect, retrieve, compare, test, repair mechanical faults, and perform adversarial verification. It cannot silently change scientific questions, hypotheses, mechanisms, endpoints, thresholds, controls, inclusion/exclusion rules, null definitions, or statistical criteria.

Ambiguous scientific decisions produce BLOCKED.

## Runtime target

V1 source architecture targets Android. The Python core is embedded through a Python-on-Android runtime (Chaquopy-compatible design). The same Python core remains portable for controlled desktop/server execution.

## Non-goals

This architecture does not claim superintelligence, unrestricted autonomy, or a complete security sandbox. Production hardening is required before granting broad repository write access.
