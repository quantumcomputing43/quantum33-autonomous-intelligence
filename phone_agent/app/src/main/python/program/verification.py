from __future__ import annotations
import hashlib, json

def verify_evidence(evidence):
    errors=[]
    for item in evidence or []:
        if not isinstance(item,dict): errors.append("invalid evidence record"); continue
        if item.get("authority") not in (None,"EVIDENCE_ONLY","EVIDENCE_OR_PROPOSAL_ONLY"):
            errors.append("evidence authority escalation detected")
    return {"status":"PASS" if not errors else "FAIL","errors":errors}

def fingerprint(payload):
    return hashlib.sha256(json.dumps(payload,sort_keys=True,default=str).encode()).hexdigest()

def verify_result(result, expected_keys=()):
    missing=[k for k in expected_keys if k not in result]
    return {"status":"PASS" if not missing else "FAIL","missing":missing}
