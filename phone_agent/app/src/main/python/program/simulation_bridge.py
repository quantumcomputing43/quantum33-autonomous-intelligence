import json
from dataclasses import dataclass
from urllib.parse import quote

@dataclass
class SimulationJob:
    project_id: str
    contract_path: str
    level: int
    command: str
    workflow: str
    ref: str = "main"

class SimulationMatrixBridge:
    """Dispatch boundary; scientific contract remains outside this transport layer."""
    def __init__(self, github_service=None):
        self.github = github_service

    def build_request(self, project_id, contract_path, level, command, workflow, ref="main"):
        if not project_id or not contract_path or not workflow:
            raise ValueError("project_id, contract_path and workflow are required")
        return SimulationJob(project_id, contract_path, int(level), command, workflow, ref)

    def build_and_dispatch(self, project_id, contract_path, level, command, workflow, ref="main"):
        job=self.build_request(project_id, contract_path, level, command, workflow, ref)
        if self.github is None:
            raise RuntimeError("GitHub service required")
        repository=self.github.current_repository
        if not repository:
            raise RuntimeError("Repository context required")
        owner, repo=repository.split("/",1)
        path=f"/repos/{owner}/{repo}/actions/workflows/{quote(job.workflow,safe='')}/dispatches"
        self.github.api.request("POST", path, {"ref":job.ref,"inputs":{
            "project_id":job.project_id,"contract_path":job.contract_path,
            "level":str(job.level),"command":job.command}})
        return {"status":"DISPATCHED","workflow":job.workflow,"ref":job.ref,
                "project_id":job.project_id,"level":job.level}

    def serialize(self, job):
        return json.dumps({"project_id":job.project_id,"contract_path":job.contract_path,
            "level":job.level,"command":job.command,"workflow":job.workflow,
            "ref":job.ref,"authority":"HUMAN_COMMAND_REQUIRED"},sort_keys=True)
