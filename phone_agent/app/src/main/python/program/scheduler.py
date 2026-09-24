from __future__ import annotations
from collections import deque
from .task_manager import TaskManager, TaskState

class Scheduler:
    def __init__(self,max_seconds=30.0):
        self.manager=TaskManager(max_seconds=max_seconds); self.queue=deque()
    def enqueue(self,name,handler):
        task=self.manager.submit(name,handler); self.queue.append(task); return task
    def run_next(self):
        if not self.queue: return None
        return self.manager.run(self.queue.popleft())
    def run_all(self):
        out=[]
        while self.queue: out.append(self.run_next())
        return out
