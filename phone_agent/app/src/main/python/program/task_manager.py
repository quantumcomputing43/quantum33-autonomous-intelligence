from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable
import time, uuid

class TaskState(str, Enum):
    PENDING="PENDING"; RUNNING="RUNNING"; COMPLETED="COMPLETED"; FAILED="FAILED"; CANCELLED="CANCELLED"

@dataclass
class Task:
    name: str
    handler: Callable
    task_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    state: TaskState = TaskState.PENDING
    result: object = None
    error: str = ""
    started_at: float | None = None
    finished_at: float | None = None

class TaskManager:
    def __init__(self, max_seconds: float = 30.0):
        self.max_seconds=max(0.1,float(max_seconds)); self.tasks={}
    def submit(self,name,handler):
        t=Task(name=name,handler=handler); self.tasks[t.task_id]=t; return t
    def run(self,t: Task):
        t.state=TaskState.RUNNING; t.started_at=time.monotonic()
        try:
            t.result=t.handler()
            elapsed=time.monotonic()-t.started_at
            if elapsed>self.max_seconds: raise TimeoutError("task resource budget exceeded")
            t.state=TaskState.COMPLETED
        except Exception as exc:
            t.error=str(exc); t.state=TaskState.FAILED
        finally: t.finished_at=time.monotonic()
        return t
    def cancel(self,t: Task):
        if t.state in (TaskState.PENDING, TaskState.RUNNING): t.state=TaskState.CANCELLED
        return t
