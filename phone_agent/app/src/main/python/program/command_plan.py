from dataclasses import dataclass

@dataclass
class Plan:
    intent: str
    read_only: bool
    tools: list
    notes: str = ""

def classify_intent(command: str) -> Plan:
    c = command.lower()
    tools = []
    if any(x in c for x in ("github", "repository", "repo", "file", "commit", "pull request", "workflow")):
        tools.append("github")
    if any(x in c for x in ("web", "search", "literature", "paper", "source", "latest")):
        tools.append("knowledge")
    if any(x in c for x in ("python", "calculate", "compute", "script")):
        tools.append("python")
    if any(x in c for x in ("simulation matrix", "simulation", "matrix", "run experiment")):
        tools.append("simulation")
    if any(x in c for x in ("quantum simulation", "quantum simulator", "superposition", "state vector")):
        tools.append("quantum_simulation")
    if not tools:
        tools.append("reasoning")
    write_like = any(x in c for x in ("write", "commit", "push", "delete", "merge", "create pull request"))
    return Plan(
        intent="multi_tool" if len(tools) > 1 else tools[0],
        read_only=not write_like,
        tools=tools,
        notes="Tool selection is routing only; it does not authorize scientific decisions."
    )
