import pytest
from core.agent import AutonomousAuditAgent
from core.command_gateway import Command
from core.policy import IssueClass, classify_issue
from core.repair_engine import RepairEngine

def test_human_command_only():
    out = AutonomousAuditAgent().execute(Command("c1","human","audit",{}))
    assert out["status"] == "ACCEPTED"

def test_non_human_blocked():
    with pytest.raises(PermissionError):
        AutonomousAuditAgent().execute(Command("c2","github_event","audit",{}))

def test_scientific_boundary():
    assert classify_issue(IssueClass.SCIENTIFIC,"threshold change").action == "BLOCK"

def test_mechanical_repair_requires_verification():
    assert RepairEngine().propose("serialization","fix JSON").verification_required
