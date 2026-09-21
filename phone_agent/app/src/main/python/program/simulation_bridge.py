import json
from dataclasses import dataclass

@dataclass
class SimulationJob:
    project_id: str
    contract_path: str
    level: int
    command: str

class SimulationMatrixBridge:
    """Transport boundary to the independent Simulation Matrix.

    This module does not invent contracts or silently change scientific parameters.
    """
    def build_request(self, project_id: str, contract_path: str, level: int, command: str):
        return SimulationJob(project_id, contract_path, int(level), command)

    def serialize(self, job: SimulationJob):
        return json.dumps({
            "project_id": job.project_id,
            "contract_path": job.contract_path,
            "level": job.level,
            "command": job.command,
            "authority": "HUMAN_COMMAND_REQUIRED",
        }, sort_keys=True)
