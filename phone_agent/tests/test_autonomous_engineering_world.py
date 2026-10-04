from program.preflight import PredictivePreflight
from program.world import EngineeringSupervisor


def test_preflight_predicts_auth_and_regression_paths():
    report = PredictivePreflight().run("demo", {"tree": [".github/workflows/build.yml", "build.gradle"]}, {})
    ids = {s["id"] for s in report.scenarios}
    assert {"S-AUTH", "S-REGRESSION"} <= ids
    assert report.required_evidence


def test_supervisor_terminal_state_is_explicit():
    s = EngineeringSupervisor(max_cycles=1).start("build demo", "demo")
    s.cycle = 1
    s2 = EngineeringSupervisor(max_cycles=1)
    s2.advance(s)
    assert s2.max_cycles == 1
    assert s.terminal()
    assert s.status == "NO_VALID_PATH"
