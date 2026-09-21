from dataclasses import dataclass

@dataclass
class SimulationRequest:
    case: str
    contract: dict
    level: int

class SimulationAdapter:
    """Interface to the independent Simulation Matrix executor."""

    def __init__(self, runner=None):
        self.runner = runner

    def execute(self, request: SimulationRequest):
        if self.runner is None:
            raise RuntimeError("Simulation Matrix runner is not configured")
        return self.runner(request.case, request.contract, request.level)
