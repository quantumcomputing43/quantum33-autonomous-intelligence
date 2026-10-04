from program.runtime import AutonomousPhoneRuntime

def test_runtime_blocks_without_model():
    runtime=AutonomousPhoneRuntime()
    result=runtime.handle_human_command("inspect the app", repository="quantumcomputing43/quantum33-autonomous-intelligence")
    assert "model backend is not configured" in result

def test_configuration_blocks_without_credentials():
    runtime=AutonomousPhoneRuntime()
    result=runtime.validate_configuration(
        "quantumcomputing43/quantum33-autonomous-intelligence",
        "quantumcomputing43/quantum33-simulation-matrix",
        "simulation-matrix.yml",
        "", "", "", ""
    )
    assert result.startswith("BLOCKED:")
