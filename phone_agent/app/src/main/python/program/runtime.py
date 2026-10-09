import json
from datetime import datetime, timezone
from pathlib import Path

from program.authority import Authority, CommandEnvelope, Decision, decide
from program.github_service import GitHubService
from program.brain import Brain, BrainContext
from program.model_provider import OpenAICompatibleBackend
from program.scientific_guard import guard_model_output
from program.memory import MemoryStore
from program.tool_executor import ToolExecutor
from program.simulation_bridge import SimulationMatrixBridge
from program.world import EngineeringSupervisor
from program.preflight import PredictivePreflight

# Safety brake only. It is not a definition of intelligence or completion.
MAX_CYCLES = 24

class AutonomousPhoneRuntime:
    """Bounded reason-act-observe-verify loop with explicit human authority."""
    def __init__(self):
        self.history=[]
        self.memory=MemoryStore(Path.home()/".quantum33_agent")
        self.supervisor=EngineeringSupervisor(MAX_CYCLES)
        self.preflight=PredictivePreflight()

    def validate_configuration(self, source_repo, simulation_repo, simulation_workflow,
                               github_token, model_endpoint, model_name, model_api_key):
        checks=[]
        if not github_token:
            checks.append(("GitHub credential","BLOCKED","missing token"))
        else:
            try:
                gh=GitHubService(github_token)
                src=gh.repository(source_repo)
                src_perms=src.get("permissions") or {}
                if src_perms and src_perms.get("push") is False:
                    checks.append(("Agent source repo","BLOCKED","GitHub credential lacks push permission"))
                else:
                    checks.append(("Agent source repo","PASS",src.get("full_name",source_repo)))
                sim=gh.repository(simulation_repo)
                sim_perms=sim.get("permissions") or {}
                if sim_perms and sim_perms.get("push") is False:
                    checks.append(("Simulation Matrix repo","BLOCKED","GitHub credential lacks repository write permission"))
                else:
                    checks.append(("Simulation Matrix repo","PASS",sim.get("full_name",simulation_repo)))
                workflow_path=simulation_workflow
                if not workflow_path.startswith(".github/workflows/"):
                    workflow_path=".github/workflows/"+workflow_path
                gh.file(simulation_repo,workflow_path)
                checks.append(("Simulation workflow","PASS",workflow_path))
            except Exception as exc:
                checks.append(("GitHub/Simulation","BLOCKED",str(exc)))
        if not (model_endpoint and model_name and model_api_key):
            checks.append(("LLM backend","BLOCKED","endpoint, model and API key are required"))
        else:
            try:
                result=OpenAICompatibleBackend(model_endpoint,model_name,model_api_key).validate()
                checks.append(("LLM backend","PASS",f"{result.get('model')} responded"))
            except Exception as exc:
                checks.append(("LLM backend","BLOCKED",str(exc)))
        ok=all(status=="PASS" for _,status,_ in checks)
        lines=["READY: all required configuration checks passed." if ok else
               "BLOCKED: configuration is not ready."]
        lines += [f"{name}: {status} — {detail}" for name,status,detail in checks]
        return "\n".join(lines)

    def handle_human_command(self, command, repository="", github_token="",
                             explicit_write_authorization=False,
                             model_endpoint="", model_name="", model_api_key="",
                             simulation_repository=""):
        command=command.strip()
        if not command:
            return "BLOCKED: empty command."
        envelope=CommandEnvelope(command,Authority.HUMAN,explicit_write_authorization)
        decision=decide(envelope)
        if decision is Decision.BLOCK:
            return self._record(command,repository,decision.value,"BLOCKED: protected scientific contract.")
        if decision is Decision.REQUIRE_HUMAN_AUTHORIZATION:
            return self._record(command,repository,decision.value,
                                "BLOCKED: explicit one-time write authorization required.")
        if not (model_endpoint and model_name and model_api_key):
            return self._record(command,repository,decision.value,
                                "BLOCKED: autonomous model backend is not configured.")

        state=self.supervisor.start(command, repository or None)
        evidence=[]
        observations=[]
        try:
            if not github_token:
                raise ValueError("GitHub credential is required for repository-aware agent operation")
            gh=GitHubService(github_token)
        except Exception as exc:
            state.set_terminal("BLOCKED")
            return self._record(command,repository,decision.value,
                                "BLOCKED: GitHub configuration unavailable: "+str(exc))

        try:
            if repository:
                evidence.append({"source":"github","kind":"repository",
                                 "content":repr(gh.repository(repository))})
            if simulation_repository:
                evidence.append({"source":"simulation","kind":"repository",
                                 "content":simulation_repository})
            tree=gh.tree(repository,"HEAD") if repository else {}
            runs=gh.workflow_runs(repository,10) if repository else {}
            report=self.preflight.run(repository or "local", tree, runs)
            evidence.append({"source":"simulation_matrix","kind":"preflight",
                             "content":repr(report.as_dict())})
            state.scenarios.extend(report.scenarios)
            state.phase="SELECT_STRATEGY" if report.status=="PREFLIGHT_CAUTION" else "EXECUTE"
        except Exception as exc:
            state.set_terminal("BLOCKED")
            return self._record(command,repository,decision.value,
                                "BLOCKED: predictive preflight failed: "+str(exc))

        try:
            backend=OpenAICompatibleBackend(model_endpoint,model_name,model_api_key)
        except Exception as exc:
            state.set_terminal("BLOCKED")
            return self._record(command,repository,decision.value,
                                "BLOCKED: model configuration error: "+str(exc))

        bridge=SimulationMatrixBridge(gh)
        executor=ToolExecutor(gh,bridge,self.memory,
                              write_authorized=explicit_write_authorization)
        memory=self.memory.search(command,repository)[:20]
        final=None
        verified=False

        while not state.terminal():
            self.supervisor.advance(state)
            if state.terminal():
                break
            state.phase="REASON"
            ctx=BrainContext(command,evidence,memory,repository or None,
                             state.cycle,observations)
            reasoning=Brain(backend).reason(ctx)
            if reasoning.get("status")!="MODEL_RESPONSE":
                state.set_terminal("BLOCKED")
                final="BLOCKED: model reasoning unavailable."
                break
            try:
                raw=ToolExecutor.parse_json_object(reasoning["response"])
                plan=ToolExecutor.parse_actions(reasoning["response"])
                if raw.get("final"):
                    candidate=str(raw["final"])
                    if self._is_verified_success(candidate, observations):
                        state.set_terminal("SUCCESS")
                        verified=True
                        final=candidate
                    else:
                        state.phase="VERIFY"
                        observations.append({"cycle":state.cycle,
                                             "kind":"verification_gate",
                                             "status":"REJECTED",
                                             "reason":"model final claim lacks observed verification evidence"})
                    if state.terminal():
                        break
                if not plan:
                    state.set_terminal("NO_VALID_PATH")
                    final="NO_VALID_PATH: no executable action plan and no verified final result."
                    break
            except Exception as exc:
                state.set_terminal("VERIFICATION_FAILED")
                final="VERIFICATION_FAILED: invalid model action plan: "+str(exc)
                break

            state.phase="EXECUTE"
            for action in plan:
                tool=action.get("tool","")
                try:
                    result=executor.execute(action)
                    obs={"cycle":state.cycle,"tool":tool,"status":"OK",
                         "result":repr(result)[:12000]}
                except PermissionError as exc:
                    obs={"cycle":state.cycle,"tool":tool,"status":"BLOCKED",
                         "error":str(exc)}
                except Exception as exc:
                    obs={"cycle":state.cycle,"tool":tool,"status":"ERROR",
                         "error":str(exc)}
                    state.failures.append(obs)
                observations.append(obs)
                self.memory.add(f"{datetime.now(timezone.utc).timestamp()}-{state.cycle}",
                                "tool_observation",json.dumps(obs,ensure_ascii=False),
                                tool,repository or None,"OBSERVED")

            state.phase="VERIFY"
            if any(o.get("status")=="ERROR" for o in observations[-len(plan):]):
                state.phase="ROOT_CAUSE"
                state.repairs.append({"cycle":state.cycle,
                                      "required":"identify root cause before repeating failed strategy"})
            memory=self.memory.search(command,repository)[:20]

        if final is None:
            final=f"{state.status}: execution reached terminal state without an unverified success claim."
        if verified:
            final="SUCCESS: "+final
        safe=guard_model_output(final)
        return self._record(command,repository,decision.value,safe["text"],steps=state.cycle)

    @staticmethod
    def _is_verified_success(candidate, observations):
        """Fail closed unless task-specific verification evidence is present."""
        text=candidate.lower()
        if not any(marker in text for marker in ("success", "completed", "done")):
            return False
        for observation in observations:
            if observation.get("kind") != "verification":
                continue
            if observation.get("status") != "PASS":
                continue
            if observation.get("goal_match") is not True:
                continue
            evidence = observation.get("evidence")
            if isinstance(evidence, list) and evidence:
                return True
        return False

    def _record(self,command,repository,decision,message,steps=0):
        row={"timestamp":datetime.now(timezone.utc).isoformat(),"command":command,
             "repository":repository,"decision":decision,"steps":steps,"status":message}
        self.history.append(row)
        self.memory.add(row["timestamp"],"command_result",message,"runtime",
                        repository or None,"RECORDED")
        return decision + ": " + message
