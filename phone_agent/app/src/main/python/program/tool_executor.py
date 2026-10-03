import json

class ToolExecutor:
    """Allow-listed tool execution. Model output never becomes authority."""
    def __init__(self, github_service=None, simulation_bridge=None, memory_store=None):
        self.github = github_service
        self.simulation = simulation_bridge
        self.memory = memory_store

    def execute(self, action):
        tool = action.get("tool")
        args = action.get("args") or {}
        if tool == "github.repository":
            return self.github.repository(args["repository"])
        if tool == "github.file":
            return self.github.file(args["repository"], args["path"], args.get("ref"))
        if tool == "github.tree":
            return self.github.tree(args["repository"], args.get("ref", "HEAD"))
        if tool == "github.commits":
            return self.github.commits(args["repository"], int(args.get("per_page", 20)))
        if tool == "github.workflow_runs":
            return self.github.workflow_runs(args["repository"], int(args.get("per_page", 20)))
        if tool == "simulation.request":
            return self.simulation.build_and_dispatch(
                project_id=args["project_id"], contract_path=args["contract_path"],
                level=int(args["level"]), command=args.get("command", ""),
                workflow=args["workflow"], ref=args.get("ref", "main"))
        if tool == "memory.search":
            if self.memory is None: return []
            return self.memory.search(args.get("text", ""), args.get("project"))
        raise ValueError("Tool not allow-listed: " + str(tool))

    @staticmethod
    def parse_actions(text):
        data = json.loads(text)
        actions = data.get("actions")
        if not isinstance(actions, list) or len(actions) > 8:
            raise ValueError("Invalid action plan: at most 8 actions")
        for a in actions:
            if not isinstance(a, dict) or not isinstance(a.get("tool"), str):
                raise ValueError("Invalid action item")
        return actions
