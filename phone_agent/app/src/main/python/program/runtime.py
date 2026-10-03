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

MAX_STEPS = 6

class AutonomousPhoneRuntime:
    """Bounded reason-act-observe-verify loop with explicit authority boundaries."""
    def __init__(self):
        self.history=[]
        self.memory=MemoryStore(Path.home()/".quantum33_agent")

    def handle_human_command(self, command, repository="", github_token="",
                             explicit_write_authorization=False,
                             model_endpoint="", model_name="", model_api_key=""):
        command=command.strip()
        if not command: return "BLOCKED: empty command."
        envelope=CommandEnvelope(command,Authority.HUMAN,explicit_write_authorization)
        decision=decide(envelope)
        if decision is Decision.BLOCK:
            return self._record(command,repository,decision.value,"BLOCKED: protected scientific contract.")
        if decision is Decision.REQUIRE_HUMAN_AUTHORIZATION:
            return self._record(command,repository,decision.value,"BLOCKED: explicit one-time write authorization required.")

        evidence=[]
        gh=None
        if github_token:
            try: gh=GitHubService(github_token)
            except Exception as exc: evidence.append({"source":"github","kind":"error","content":str(exc)})
        backend=None
        if model_endpoint and model_name and model_api_key:
            try: backend=OpenAICompatibleBackend(model_endpoint,model_name,model_api_key)
            except Exception as exc: evidence.append({"source":"model","kind":"configuration_error","content":str(exc)})
        if backend is None:
            return self._record(command,repository,decision.value,"BLOCKED: autonomous model backend is not configured.")

        if gh and repository:
            try: evidence.append({"source":"github","kind":"repository","content":repr(gh.repository(repository))})
            except Exception as exc: evidence.append({"source":"github","kind":"error","content":str(exc)})

        bridge=SimulationMatrixBridge(gh)
        executor=ToolExecutor(gh,bridge,self.memory,write_authorized=explicit_write_authorization)
        memory=self.memory.search(command,repository)[:20]
        observations=[]
        final=None

        for step in range(1,MAX_STEPS+1):
            ctx=BrainContext(command,evidence,memory,repository or None,step,observations)
            reasoning=Brain(backend).reason(ctx)
            if reasoning.get("status")!="MODEL_RESPONSE":
                final="BLOCKED: model reasoning unavailable."
                break
            try:
                plan=json.loads(reasoning["response"])
                actions=plan.get("actions",[])
                if not isinstance(actions,list) or len(actions)>8: raise ValueError("invalid action plan")
                if plan.get("final"):
                    final=str(plan["final"]); break
            except Exception as exc:
                final="INCONCLUSIVE: invalid model action plan: "+str(exc)
                break

            if not actions:
                final="INCONCLUSIVE: agent returned no action and no final result."
                break

            for action in actions:
                tool=action.get("tool","")
                if tool.startswith("github.") and tool not in {
                    "github.repository","github.file","github.tree",
                    "github.commits","github.workflow_runs",
                    "github.create_file","github.update_file"}:
                    final="BLOCKED: GitHub tool is not allow-listed in this runtime."
                    break
                try:
                    result=executor.execute(action)
                    obs={"step":step,"tool":tool,"status":"OK","result":repr(result)[:12000]}
                except Exception as exc:
                    obs={"step":step,"tool":tool,"status":"ERROR","error":str(exc)}
                observations.append(obs)
                self.memory.add(
                    f"{datetime.now(timezone.utc).timestamp()}-{step}",
                    "tool_observation",json.dumps(obs,ensure_ascii=False),
                    tool,repository or None,"OBSERVED")
            if final: break

        if final is None:
            final="INCONCLUSIVE: maximum autonomous steps reached without verified completion."
        safe=guard_model_output(final)
        return self._record(command,repository,decision.value,safe["text"],steps=len(observations))

    def _record(self,command,repository,decision,message,steps=0):
        row={"timestamp":datetime.now(timezone.utc).isoformat(),"command":command,
             "repository":repository,"decision":decision,"steps":steps,"status":message}
        self.history.append(row)
        self.memory.add(row["timestamp"],"command_result",message,"runtime",repository or None,"RECORDED")
        return decision + ": " + message
