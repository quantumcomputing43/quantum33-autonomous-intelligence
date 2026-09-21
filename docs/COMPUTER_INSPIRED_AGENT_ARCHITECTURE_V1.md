# Computer-Inspired Autonomous Agent Architecture V1

## Purpose
Translate proven computer-system separation of concerns into the phone-hosted
autonomous agent without pretending the agent is a computer or granting
unrestricted authority.

## System mapping
| Computer concept | Agent component | Role |
|---|---|---|
| CPU | Reasoning + execution coordinator | Decompose and execute authorized work |
| RAM | Working context | Current task, evidence, active intermediate state |
| Storage | Persistent memory + project workspace | Durable knowledge, checkpoints, provenance |
| OS kernel | Authority/policy + orchestrator | Resource and permission boundary |
| Processes | Isolated tasks | Independent work units with lifecycle/status |
| Scheduler | Task planner | Dependencies, ordering, stopping |
| Cache | Context/evidence cache | Reuse verified information without pretending it is fresh |
| File system | Project-scoped workspace | Isolation and reproducible artifacts |
| Device drivers | Tool adapters | Uniform interfaces to GitHub/search/Python/simulation |
| I/O | Tool layer | External data and services |
| Interrupts | Event/error/alert bus | Failures, blockers, completion and recovery triggers |
| GPU/accelerator | Specialized computation engines | Simulation, numerical and quantum-inspired modules |
| Diagnostics | Verification + adversarial audit | Detect false success and integrity failures |
| Boot/recovery | Checkpoint/recovery manager | Resume from verified state |
| Security model | Command authority + scoped permissions | Human authority and fail-closed boundaries |
| Network stack | External knowledge/connectivity | Optional remote capabilities |

## Operating architecture

Human
-> Command Gateway
-> Agent Kernel/Orchestrator
-> Planner/Scheduler
-> Working Memory
-> Tool Router
-> Tool Adapters / Local Compute
-> Evidence + Provenance
-> Verification
-> Persistent Memory / Checkpoint
-> Report

Reasoning is a service inside this system, not the authority. External content,
model output and tool output are data/evidence only.

## Required kernel properties
1. Deterministic command acceptance and authorization.
2. Project isolation and explicit task identity.
3. Bounded working memory and resource budgets.
4. Allowlisted tools with explicit capability metadata.
5. Evidence provenance and integrity hashes.
6. Checkpointable task state.
7. Failure states distinct from scientific conclusions.
8. Verification before material completion.
9. Adversarial verification for high-impact results.
10. Explicit stop/block conditions.
11. Recovery after process interruption.
12. No automatic instruction execution from external content.

## Current gap audit
The current construction already has command authority, orchestration,
memory/provenance, ledger, tool routing, model backend and local
quantum-inspired computation. The following remain construction targets before
a final APK release:
- persistent encrypted working/persistent memory integration
- task/process lifecycle and scheduler
- project snapshot/checkpoint manager wired into runtime
- unified tool adapter registry for all capabilities
- resource/time budgets and cancellation
- verification pipeline attached to material actions
- crash recovery and resumable checkpoints
- event/alert mechanism
- adversarial verification harness
- end-to-end offline self-test
- final Android build plus runtime verification

These are architecture requirements, not claims that the missing components
already operate.

## Integrity boundary
This architecture may increase autonomy in decomposition, inspection,
computation, verification and recovery. It must not allow the agent to invent
or silently change scientific hypotheses, endpoints, thresholds, controls, null
definitions or other scientific contract elements.

## Non-claim
This is a computer-inspired software architecture. It is not a claim of
general intelligence, consciousness, quantum computing, or quantum advantage.
