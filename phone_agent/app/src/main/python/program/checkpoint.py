from __future__ import annotations
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone

class CheckpointStore:
    def __init__(self, root=None):
        self.root=Path(root or (Path.cwd()/".quantum33")); self.root.mkdir(parents=True,exist_ok=True)
    def save(self,task_id,state,payload):
        item={"task_id":task_id,"state":state,"payload":payload,"saved_at":datetime.now(timezone.utc).isoformat()}
        item["sha256"]=hashlib.sha256(json.dumps(item,sort_keys=True,default=str).encode()).hexdigest()
        p=self.root/f"checkpoint_{task_id}.json"; p.write_text(json.dumps(item,sort_keys=True,default=str),encoding="utf-8"); return p
    def load(self,task_id):
        p=self.root/f"checkpoint_{task_id}.json"
        if not p.exists(): return None
        item=json.loads(p.read_text(encoding="utf-8")); expected=item.pop("sha256",None)
        actual=hashlib.sha256(json.dumps(item,sort_keys=True,default=str).encode()).hexdigest()
        if expected!=actual: raise ValueError("checkpoint integrity failure")
        return item
