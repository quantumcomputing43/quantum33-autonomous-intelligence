from program.authority import Authority, CommandEnvelope, Decision, decide
from program.checkpoint import CheckpointStore
from program.provenance import normalize_evidence
from program.verification import verify_evidence, verify_result
from program.task_manager import TaskManager, TaskState

def run():
    assert decide(CommandEnvelope("change hypothesis",Authority.HUMAN)) is Decision.BLOCK
    assert decide(CommandEnvelope("inspect repository",Authority.EXTERNAL)) is Decision.BLOCK
    assert verify_evidence([{"authority":"EVIDENCE_ONLY"}])["status"]=="PASS"
    assert verify_evidence([{"authority":"HUMAN"}])["status"]=="FAIL"
    assert verify_result({"ok":1},["ok"])["status"]=="PASS"
    assert verify_result({},["ok"])["status"]=="FAIL"
    tm=TaskManager(max_seconds=1)
    t=tm.submit("ok",lambda: 42); assert tm.run(t).state is TaskState.COMPLETED
    c=CheckpointStore(); p=c.save(t.task_id,t.state.value,{"value":42}); assert c.load(t.task_id)["payload"]["value"]==42
    raw=p.read_text(); p.write_text(raw.replace('"value": 42','"value": 43'),encoding="utf-8")
    try: c.load(t.task_id); raise AssertionError("tampered checkpoint accepted")
    except ValueError: pass
    return {"status":"PASS","checks":10}
