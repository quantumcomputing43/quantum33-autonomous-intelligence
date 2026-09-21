from dataclasses import dataclass
from typing import Callable


@dataclass
class ToolSpec:
    name: str
    description: str
    handler: Callable
    enabled: bool = True


class ToolRouter:
    def __init__(self):
        self._tools = {}

    def register(self, spec: ToolSpec):
        if not callable(spec.handler):
            raise TypeError("Tool handler must be callable")
        self._tools[spec.name] = spec

    def enabled(self):
        return {k: v for k, v in self._tools.items() if v.enabled}

    def call(self, name, *args, **kwargs):
        spec = self._tools.get(name)
        if spec is None or not spec.enabled:
            raise PermissionError(f"Tool not enabled: {name}")
        return spec.handler(*args, **kwargs)

    # Compatibility alias for older orchestration code.
    def run(self, name, *args, **kwargs):
        return self.call(name, *args, **kwargs)
