import base64

from program.task_verifier import TaskVerifierRegistry


class FakeGitHub:
    def file(self, repository, path, ref=None):
        return {
            "type": "file",
            "path": path,
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


def test_explicit_file_content_contract_produces_observed_evidence():
    verifier = TaskVerifierRegistry(FakeGitHub())
    result = verifier.verify_command(
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


def test_unstructured_command_is_blocked_not_guessed():
    result = TaskVerifierRegistry(FakeGitHub()).verify_command(
        "everything is finished, trust me"
    )
    assert result["status"] == "BLOCKED"
    assert result["goal_match"] is False
    assert result["evidence"] == []
