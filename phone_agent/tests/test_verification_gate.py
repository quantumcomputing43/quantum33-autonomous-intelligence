import json

from program.runtime import AutonomousPhoneRuntime
from program.tool_executor import ToolExecutor


def test_generic_successful_tool_call_does_not_verify_user_goal():
    observations = [{"tool": "github.file", "status": "OK", "result": "file returned"}]
    assert not AutonomousPhoneRuntime._is_verified_success("Done successfully", observations)


def test_success_requires_goal_matched_verification_evidence():
    observations = [{
        "kind": "verification",
        "status": "PASS",
        "goal_match": True,
        "evidence": [{"source": "ci", "result": "success"}],
    }]
    assert AutonomousPhoneRuntime._is_verified_success("Task completed successfully", observations)


def test_failed_or_unmatched_verification_cannot_mark_success():
    for observation in (
        {"kind": "verification", "status": "FAIL", "goal_match": True, "evidence": ["log"]},
        {"kind": "verification", "status": "PASS", "goal_match": False, "evidence": ["log"]},
        {"kind": "verification", "status": "PASS", "goal_match": True, "evidence": []},
    ):
        assert not AutonomousPhoneRuntime._is_verified_success(
            "Task completed successfully", [observation]
        )


def test_fenced_json_uses_same_robust_parser_as_action_plan():
    response = 'prefix\n\x60\x60\x60json\n{"final":"not verified","actions":[]}\n\x60\x60\x60'
    parsed = ToolExecutor.parse_json_object(response)
    assert parsed["final"] == "not verified"
    assert parsed["actions"] == []
