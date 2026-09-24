from __future__ import annotations
class ResourceBudget:
    def __init__(self,max_tasks=32,max_seconds=30.0):
        self.max_tasks=int(max_tasks); self.max_seconds=float(max_seconds)
    def accept(self,current_tasks):
        return current_tasks < self.max_tasks
