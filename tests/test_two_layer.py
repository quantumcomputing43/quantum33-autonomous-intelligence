from pathlib import Path

from program.python_executor import PythonExecutor
from simulation.contracts import SimulationContract, SimulationEngine, SimulationResult


def test_simulation_contract_blocks_missing_thresholds():
    contract = SimulationContract(
        simulation_id="demo",
        hypothesis="test",
        inputs={},
        metrics=("m",),
        thresholds={},
    )
    try:
        contract.validate()
    except ValueError as exc:
        assert "thresholds" in str(exc)
    else:
        raise AssertionError("Incomplete scientific contract must block")


def test_python_executor_runs_python_without_shell(tmp_path: Path):
    script = tmp_path / "hello.py"
    script.write_text("print('ok')
", encoding="utf-8")
    result = PythonExecutor().run_script(script)
    assert result.returncode == 0
    assert result.stdout.strip() == "ok"


def test_simulation_engine_requires_result():
    contract = SimulationContract(
        simulation_id="demo",
        hypothesis="test",
        inputs={},
        metrics=("m",),
        thresholds={"m": 0},
    )

    result = SimulationEngine().execute(
        contract,
        lambda c: SimulationResult(c.simulation_id, "PASS", {"m": 1}),
    )
    assert result.status == "PASS"
