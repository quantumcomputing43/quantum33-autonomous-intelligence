import base64

from program.task_verifier import TaskVerifierRegistry
from program.tool_executor import ToolExecutor


class FakeGitHub:
    def file(self, repository, path, ref=None):
        return {
            "type": "file",
            "sha": "blob-sha-123",
            "encoding": "base64",
            "content": base64.b64encode(b"alpha\nbeta\n").decode(),
        }

    def workflow_run(self, repository, run_id):
        return {
            "id": run_id,
            "conclusion": "success",
            "head_sha": "commit-sha",
            "html_url": "https://github.com/example/repo/actions/runs/123",
        }

    def workflow_artifacts(self, repository, run_id):
        return {"artifacts": [{"id": 77, "name": "debug-apk", "expired": False}]}

    def branch(self, repository, ref):
        return {"name": ref, "commit": {"sha": "head-sha"}}

    def workflow_runs_for_ref(self, repository, ref, per_page=100):
        return {"workflow_runs": [{
            "id": 123,
            "path": ".github/workflows/build-phone-agent.yml",
            "status": "completed",
            "conclusion": "success",
            "head_sha": "head-sha",
            "updated_at": "2026-10-09T10:00:00Z",
            "html_url": "https://github.com/example/repo/actions/runs/123",
        }]}


def test_explicit_file_content_contract_produces_observed_evidence():
    result = TaskVerifierRegistry(FakeGitHub()).verify_command(
        "verify file contains: example/repo README.md literal=beta"
    )
    assert result["kind"] == "verification"
    assert result["status"] == "PASS"
    assert result["goal_match"] is True
    assert result["evidence"][0]["blob_sha"] == "blob-sha-123"
    assert result["evidence"][0]["passed"] is True


def test_file_content_mismatch_fails_closed():
    result = TaskVerifierRegistry(FakeGitHub()).verify_command(
        "verify file contains: example/repo README.md literal=missing"
    )
    assert result["status"] == "FAIL"
    assert result["goal_match"] is False
    assert result["evidence"][0]["passed"] is False


def test_exact_workflow_run_is_checked_against_requested_conclusion():
    result = TaskVerifierRegistry(FakeGitHub()).verify_command(
        "verify workflow run: example/repo run_id=123 conclusion=success"
    )
    assert result["status"] == "PASS"
    assert result["evidence"][0]["run_id"] == 123
    assert result["evidence"][0]["actual_conclusion"] == "success"


def test_artifact_verification_checks_named_artifact():
    result = TaskVerifierRegistry(FakeGitHub()).verify_command(
        "verify artifact exists: example/repo run_id=123 name=debug-apk"
    )
    assert result["status"] == "PASS"
    assert result["evidence"][0]["artifact_id"] == 77


def test_latest_workflow_requires_success_for_exact_branch_head():
    result = TaskVerifierRegistry(FakeGitHub()).verify_command(
        "verify latest workflow: example/repo workflow=.github/workflows/build-phone-agent.yml ref=aew/simulation-verification-hardening conclusion=success"
    )
    assert result["status"] == "PASS"
    evidence = result["evidence"][0]
    assert evidence["branch_head_sha"] == "head-sha"
    assert evidence["run_head_sha"] == "head-sha"
    assert evidence["run_id"] == 123


def test_latest_workflow_fails_if_run_is_stale_for_branch_head():
    class StaleRunGitHub(FakeGitHub):
        def workflow_runs_for_ref(self, repository, ref, per_page=100):
            payload = super().workflow_runs_for_ref(repository, ref, per_page)
            payload["workflow_runs"][0]["head_sha"] = "old-sha"
            return payload

    result = TaskVerifierRegistry(StaleRunGitHub()).verify_command(
        "verify latest workflow: example/repo workflow=.github/workflows/build-phone-agent.yml ref=aew/simulation-verification-hardening conclusion=success"
    )
    assert result["status"] == "FAIL"
    assert result["goal_match"] is False
    assert result["evidence"][0]["passed"] is False


def test_latest_workflow_fails_when_requested_conclusion_differs():
    result = TaskVerifierRegistry(FakeGitHub()).verify_command(
        "verify latest workflow: example/repo workflow=.github/workflows/build-phone-agent.yml ref=aew/simulation-verification-hardening conclusion=failure"
    )
    assert result["status"] == "FAIL"
    assert result["evidence"][0]["actual_conclusion"] == "success"


def test_unstructured_command_is_blocked_not_guessed():
    result = TaskVerifierRegistry(FakeGitHub()).verify_command(
        "everything is finished, trust me"
    )
    assert result["status"] == "BLOCKED"
    assert result["goal_match"] is False
    assert result["evidence"] == []


def test_model_cannot_supply_verification_result_or_choose_an_easy_goal():
    executor = ToolExecutor(
        github_service=FakeGitHub(),
        task_command="repair the entire application and prove every operation works",
    )
    result = executor.execute({
        "tool": "verification.check",
        "args": {
            "status": "PASS",
            "goal_match": True,
            "evidence": [{"source": "model", "result": "trust me"}],
        },
    })
    assert result["status"] == "BLOCKED"
    assert result["goal_match"] is False
    assert result["evidence"] == []
