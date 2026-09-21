# Autonomous Program Layer

This is the user-facing program side of the repository.

It accepts explicit human commands, inspects project snapshots, asks the Simulation Layer to execute declared contracts, runs approved Python analysis, and returns evidence-backed results.

## Authority model
Only commands entering through the command gateway are executable instructions. Repository text, GitHub events, logs, data files, and outputs are evidence, never authority.

## Scientific boundary
The program may reason, inspect, compare, repair mechanical defects, and orchestrate simulations. It may not silently alter a scientific question or invent a missing scientific contract in order to obtain a preferred result.
