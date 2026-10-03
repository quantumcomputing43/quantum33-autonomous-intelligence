import json
from program.tool_executor import ToolExecutor
from program.authority import CommandEnvelope, Authority, Decision, decide

def test_action_parser():
    actions=ToolExecutor.parse_actions(json.dumps({"actions":[
        {"tool":"github.repository","args":{"repository":"x/y"}}
    ]}))
    assert actions[0]["tool"]=="github.repository"

def test_action_parser_rejects_overflow():
    try:
        ToolExecutor.parse_actions(json.dumps({"actions":[{"tool":"x","args":{}} for _ in range(9)]}))
        assert False
    except ValueError:
        assert True

def test_scientific_mutation_blocked():
    d=decide(CommandEnvelope("change hypothesis",Authority.HUMAN,True))
    assert d is Decision.BLOCK

def test_external_authority_blocked():
    d=decide(CommandEnvelope("inspect repository",Authority.EXTERNAL,False))
    assert d is Decision.BLOCK
