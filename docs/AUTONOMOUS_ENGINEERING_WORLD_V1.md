# Autonomous Engineering World V1

## Mission

Transform Quantum33 from a command-driven forensic/simulation application into a general-purpose autonomous software engineering environment.

The Android application is the interface. The engineering world is the runtime model.

## System roles

- Human: defines goals and retains final authority over consequential external actions.
- World Supervisor: maintains global task/world state and coordinates agents.
- Simulation Matrix: predictive planning, self-questioning, scenario generation, falsification, risk discovery, and strategy selection before execution.
- Codex/Executor: performs implementation actions in the configured workspace.
- GitHub Workspace: versioned source, branches, CI, artifacts, and evidence.
- Specialist Agents: architecture, coding, testing, debugging, security, build, documentation, and project adapters.
- Verification Engine: determines whether a requested outcome is actually achieved.
- Memory/Evidence: records plans, observations, failures, repairs, and verification evidence.

## Operating loop

GOAL
-> DISCOVER
-> SELF-QUESTION
-> PREFLIGHT
-> SIMULATE
-> SELECT STRATEGY
-> EXECUTE
-> OBSERVE
-> VERIFY
-> ROOT-CAUSE ANALYSIS
-> REPAIR
-> RE-VERIFY
-> LEARN
-> COMPLETE / BLOCKED / NO_VALID_PATH / NEEDS_HUMAN_DECISION

## Simulation Matrix contract

Before major execution, the Matrix should attempt to identify:

1. missing information and whether it can be discovered automatically;
2. dependency and environment incompatibilities;
3. repository and file-structure risks;
4. authentication and permission requirements;
5. build/test/tool availability;
6. likely failure modes and their detectors;
7. alternative implementation strategies;
8. regression risks;
9. repair strategies;
10. verification evidence required for success.

The Matrix should challenge the proposed plan before Codex executes it.

## Autonomous questioning

Questions that can be answered from the workspace, repository, configuration, tests, or available tools must be answered autonomously.

Only unresolved consequential decisions should reach the human.

## Adaptive execution

Do not use an arbitrary fixed step count as the definition of intelligence or completion.

Terminal states are:

- SUCCESS
- BLOCKED
- NO_VALID_PATH
- NEEDS_HUMAN_DECISION
- UNSAFE_OPERATION
- VERIFICATION_FAILED

## Evolution

The environment may improve its engineering strategies from observed failures and successful repairs, but it must not silently weaken verification, authorization, security, or frozen scientific contracts.

For scientific projects, hypotheses, endpoints, nulls, thresholds, controls, seeds, and evaluation criteria remain protected unless explicitly changed by the human.

## Generality

Project type is discovered rather than assumed. The environment should support, through adapters and verified toolchains:

- Web
- Python
- JavaScript/TypeScript
- Android
- APIs/backend
- CLI
- automation
- data/scientific software
- future project types

## World model

Each task has a persistent state containing:

- goal
- project
- actors/agents
- capabilities
- permissions
- plan
- simulation scenarios
- observations
- artifacts
- failures
- repairs
- verification evidence
- terminal status

The architecture is inspired by branching/parallel state exploration. It is not a claim of quantum computation.

## Implementation rule

Do not patch isolated symptoms when a structural design change is required.

Every material repair should answer:

- What failed?
- Why did the system allow the failure?
- How could the failure have been predicted?
- What architectural control prevents recurrence?
- What test proves the repair?
