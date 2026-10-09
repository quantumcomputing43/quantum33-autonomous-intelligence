import json
from program.task_verifier import TaskVerifierRegistry

class ToolExecutor:
    """Allow-listed execution. Repository writes and workflow dispatches require explicit human authorization."""
    def __init__(self, github_service=None, simulation_bridge=None, memory_store=None, write_authorized=False, task_command=""):
        self.github=github_service; self.simulation=simulation_bridge
        self.memory=memory_store; self.write_authorized=bool(write_authorized)
        self.task_command = str(task_command)
        self.verifier = TaskVerifierRegistry(github_service) if github_service is not None else None

    def execute(self, action):
        tool=action.get("tool"); args=action.get("args") or {}
        if tool=="github.repository": return self.github.repository(args["repository"])
        if tool=="github.file": return self.github.file(args["repository"],args["path"],args.get("ref"))
        if tool=="github.tree": return self.github.tree(args["repository"],args.get("ref","HEAD"))
        if tool=="github.commits": return self.github.commits(args["repository"],int(args.get("per_page",20)))
        if tool=="github.workflow_runs": return self.github.workflow_runs(args["repository"],int(args.get("per_page",20)))
        if tool=="github.workflow_jobs": return self.github.workflow_jobs(args["repository"],int(args["run_id"]))
        if tool=="github.workflow_artifacts": return self.github.workflow_artifacts(args["repository"],int(args["run_id"]))
        if tool=="github.create_file":
            self._write(); return self.github.create_file(args["repository"],args["path"],args["content"],args["message"],args.get("branch","main"))
        if tool=="github.update_file":
            self._write(); return self.github.update_file(args["repository"],args["path"],args["content"],args["message"],args["sha"],args.get("branch","main"))
        if tool=="github.workflow_dispatch":
            self._write(); return self.github.workflow_dispatch(args["repository"],args["workflow"],args.get("ref","main"),args.get("inputs"))
        if tool=="simulation.request":
            self._write()
            return self.simulation.build_and_dispatch(
                args["project_id"],args["contract_path"],int(args["level"]),args.get("command",""),
                args["workflow"],args["repository"],args.get("ref","main"))
        if tool=="verification.check":
            if self.verifier is None:
                raise RuntimeError("Task verification service is unavailable")
            return self.verifier.verify_command(self.task_command)
        if tool=="memory.search":
            return [] if self.memory is None else self.memory.search(args.get("text",""),args.get("project"))
        raise ValueError("Tool not allow-listed: "+str(tool))

    def _write(self):
        if not self.write_authorized:
            raise PermissionError("Explicit human write authorization required")

    @staticmethod
    def parse_actions(text):
        data=ToolExecutor.parse_json_object(text)
        actions=data.get("actions")
        if not isinstance(actions,list) or len(actions)>8:
            raise ValueError("Invalid action plan")
        for a in actions:
            if not isinstance(a,dict) or not isinstance(a.get("tool"),str):
                raise ValueError("Invalid action")
            if "args" in a and not isinstance(a.get("args"),dict):
                raise ValueError("Invalid action args")
        return actions

    @staticmethod
    def parse_json_object(text):
        if not isinstance(text,str) or not text.strip():
            raise ValueError("Empty model response")
        candidate=text.strip()
        if candidate.startswith("```"):
            parts=candidate.splitlines()
            if parts and parts[0].strip().startswith("```"): parts=parts[1:]
            if parts and parts[-1].strip()=="```": parts=parts[:-1]
            candidate="\n".join(parts).strip()
        try:
            data=json.loads(candidate)
        except json.JSONDecodeError:
            start=candidate.find("{"); end=candidate.rfind("}")
            if start < 0 or end <= start: raise ValueError("Model did not return a JSON object")
            try: data=json.loads(candidate[start:end+1])
            except json.JSONDecodeError as exc: raise ValueError("Invalid model JSON: "+str(exc)) from exc
        if not isinstance(data,dict): raise ValueError("Model JSON root must be an object")
        return data
