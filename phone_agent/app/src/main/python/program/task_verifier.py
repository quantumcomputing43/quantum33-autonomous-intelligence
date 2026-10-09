"""Deterministic, allow-listed task verification.

Verification contracts are explicit and machine-checkable. Model prose is never evidence.
Unsupported contracts fail closed rather than falling back to a model-authored PASS.
"""
import base64
import hashlib
import re


class TaskVerifierRegistry:
    def __init__(self, github_service):
        self.github = github_service

    @staticmethod
    def parse_contract(command):
        """Parse only explicit verification commands; do not infer success criteria."""
        text = command.strip()
        patterns = (
            (r'^verify file exists: (?P<repo>[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+) (?P<path>[^\s]+)(?: ref=(?P<ref>[A-Za-z0-9_./-]+))?$', "file_exists"),
            (r'^verify file contains: (?P<repo>[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+) (?P<path>[^\s]+) literal=(?P<literal>.+)$', "file_contains"),
            (r'^verify workflow run: (?P<repo>[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+) run_id=(?P<run_id>[0-9]+) conclusion=(?P<conclusion>success|failure|cancelled|timed_out)$', "workflow_run"),
            (r'^verify artifact exists: (?P<repo>[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+) run_id=(?P<run_id>[0-9]+) name=(?P<name>[^\s]+)$', "artifact_exists"),
            (r'^verify latest workflow: (?P<repo>[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+) workflow=(?P<workflow>[^\s]+) ref=(?P<ref>[A-Za-z0-9_./-]+) conclusion=(?P<conclusion>success|failure|cancelled|timed_out)$', "latest_workflow"),
        )
        for pattern, kind in patterns:
            match = re.fullmatch(pattern, text, flags=re.IGNORECASE)
            if match:
                contract = match.groupdict()
                contract["type"] = kind
                contract["requested_command_sha256"] = hashlib.sha256(text.encode("utf-8")).hexdigest()
                if contract.get("conclusion"):
                    contract["conclusion"] = contract["conclusion"].lower()
                return contract
        return None

    def verify_command(self, command):
        contract = self.parse_contract(command)
        if contract is None:
            return {
                "kind": "verification",
                "status": "BLOCKED",
                "goal_match": False,
                "evidence": [],
                "reason": "No supported explicit verification contract; task remains unverified.",
            }
        repo = contract["repo"]
        try:
            if contract["type"] in ("file_exists", "file_contains"):
                response = self.github.file(repo, contract["path"], contract.get("ref"))
                if not isinstance(response, dict) or response.get("type") != "file":
                    return self._result(contract, False, "GitHub contents endpoint did not return a file.")
                raw = response.get("content", "")
                if response.get("encoding") == "base64":
                    content = base64.b64decode(raw).decode("utf-8", errors="replace")
                else:
                    content = str(raw)
                if contract["type"] == "file_exists":
                    passed = True
                    detail = "Requested repository path exists and is a file."
                else:
                    passed = contract["literal"] in content
                    detail = "Expected literal found in file." if passed else "Expected literal not found in file."
                evidence = [{
                    "source": "github.contents",
                    "repository": repo,
                    "path": contract["path"],
                    "ref": contract.get("ref"),
                    "blob_sha": response.get("sha"),
                    "content_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
                    "check": contract["type"],
                    "passed": passed,
                }]
                return self._result(contract, passed, detail, evidence)

            if contract["type"] == "workflow_run":
                run = self.github.workflow_run(repo, int(contract["run_id"]))
                if not isinstance(run, dict) or str(run.get("id")) != contract["run_id"]:
                    return self._result(contract, False, "Requested workflow run ID did not match the GitHub response.")
                actual = str(run.get("conclusion") or run.get("status") or "").lower()
                passed = actual == contract["conclusion"]
                evidence = [{
                    "source": "github.actions.workflow_run",
                    "repository": repo,
                    "run_id": int(contract["run_id"]),
                    "html_url": run.get("html_url"),
                    "head_sha": run.get("head_sha"),
                    "actual_conclusion": actual,
                    "expected_conclusion": contract["conclusion"],
                    "passed": passed,
                }]
                return self._result(contract, passed, "Workflow conclusion checked against exact GitHub run.", evidence)

            if contract["type"] == "latest_workflow":
                branch = self.github.branch(repo, contract["ref"])
                branch_sha = ((branch.get("commit") or {}).get("sha")
                              if isinstance(branch, dict) else None)
                payload = self.github.workflow_runs_for_ref(repo, contract["ref"])
                runs = payload.get("workflow_runs", []) if isinstance(payload, dict) else []
                wanted = contract["workflow"].split("@", 1)[0]
                matches = [
                    run for run in runs
                    if str(run.get("path", "")).split("@", 1)[0] == wanted
                    and run.get("status") == "completed"
                ]
                matches.sort(key=lambda run: str(run.get("updated_at", "")), reverse=True)
                latest = matches[0] if matches else None
                actual = str((latest or {}).get("conclusion") or "").lower()
                run_sha = (latest or {}).get("head_sha")
                passed = bool(branch_sha and latest and run_sha == branch_sha
                              and actual == contract["conclusion"])
                evidence = [{
                    "source": "github.actions.latest_workflow_for_ref",
                    "repository": repo,
                    "workflow": wanted,
                    "ref": contract["ref"],
                    "branch_head_sha": branch_sha,
                    "run_id": (latest or {}).get("id"),
                    "run_head_sha": run_sha,
                    "actual_conclusion": actual or None,
                    "expected_conclusion": contract["conclusion"],
                    "run_url": (latest or {}).get("html_url"),
                    "passed": passed,
                }]
                detail = ("Latest completed workflow run matches branch HEAD and requested conclusion."
                          if passed else
                          "No qualifying run for current branch HEAD, or latest run conclusion differs.")
                return self._result(contract, passed, detail, evidence)

            if contract["type"] == "artifact_exists":
                payload = self.github.workflow_artifacts(repo, int(contract["run_id"]))
                artifacts = payload.get("artifacts", []) if isinstance(payload, dict) else []
                artifact = next((item for item in artifacts if item.get("name") == contract["name"]), None)
                passed = artifact is not None and not artifact.get("expired", False)
                evidence = [{
                    "source": "github.actions.artifacts",
                    "repository": repo,
                    "run_id": int(contract["run_id"]),
                    "artifact_name": contract["name"],
                    "artifact_id": artifact.get("id") if artifact else None,
                    "expired": artifact.get("expired") if artifact else None,
                    "passed": passed,
                }]
                return self._result(contract, passed, "Artifact existence and expiry checked against GitHub API.", evidence)
        except Exception as exc:
            return self._result(contract, False, "Verification API error: " + str(exc))
        return self._result(contract, False, "Unsupported verification type.")

    @staticmethod
    def _result(contract, passed, detail, evidence=None):
        return {
            "kind": "verification",
            "status": "PASS" if passed else "FAIL",
            "goal_match": bool(passed),
            "contract_type": contract["type"],
            "requested_command_sha256": contract["requested_command_sha256"],
            "evidence": evidence or [],
            "detail": detail,
        }
