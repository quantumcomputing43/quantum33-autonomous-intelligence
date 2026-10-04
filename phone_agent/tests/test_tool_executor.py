from program.tool_executor import ToolExecutor

class DummyGitHub:
    def update_file(self, *args, **kwargs):
        return "updated"

def test_write_is_blocked_without_authorization():
    ex = ToolExecutor(github_service=DummyGitHub(), write_authorized=False)
    try:
        ex.execute({"tool":"github.update_file","args":{}})
        assert False, "expected PermissionError"
    except PermissionError:
        pass

def test_action_limit_parser():
    actions=[{"tool":"memory.search","args":{}}]*8
    parsed=ToolExecutor.parse_actions('{"actions":'+__import__("json").dumps(actions)+'}')
    assert len(parsed)==8
